import random
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Prefetch, F
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect

from core import send_tracking_code_sms
from notifications.services import notify_user
from orders.forms import DiscountForm
from orders.models import Order, OrderItem, VendorOrder
from orders.services import OrderCalculator
from orders.services.cart_service import CartManager, CartAction
from services.models import Option, Schedule, Service
from wallet.models import WalletTransaction


@login_required
def user_cart(request: HttpRequest):
    order, _ = Order.objects.prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option', 'schedule'))
    ).get_or_create(is_paid=False, user=request.user)

    cart_manager = CartManager(order)

    alerts, order = cart_manager.enforce_capacity_constraints()
    order = cart_manager.cleanup_order_if_invalid() if order else None
    calc = OrderCalculator(order) if order else None

    context = {
        'orders': order,
        'sum': calc.total_price() if calc else 0,
        'discount_amount': calc.discount_amount() if calc else 0,
        'final_price': calc.final_price() if calc else 0,
        'alerts': alerts,
    }
    return render(request, 'orders/cart.html', context)


def add_service_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'not_auth',
            'message': 'برای افزودن به سبد خرید ابتدا وارد حساب شوید.',
            'login_url': reverse('auth_page')
        })

    service_id = request.GET.get('service_id')
    option_id = request.GET.get('option_id')
    count = int(request.GET.get('count', 1))
    schedule_id = request.GET.get('schedule_id')

    if count < 1:
        return JsonResponse({'status': 'invalid_count', 'message': 'تعداد معتبر نیست'})

    service = Service.objects.filter(id=service_id).first()
    option = Option.objects.filter(id=option_id).first()

    if not service or not option:
        return JsonResponse({'status': 'not_found', 'message': 'پارامترهای ورودی نامعتبر است'})

    active_schedules = service.schedules.filter(is_active=True)

    if active_schedules.exists():
        if not schedule_id:
            return JsonResponse({'status': 'error', 'message': 'انتخاب زمان الزامی است'})
        schedule = Schedule.objects.filter(id=schedule_id, service=service).first()
        if not schedule:
            return JsonResponse({'status': 'not_found', 'message': 'زمان انتخابی نامعتبر است'})
    else:
        schedule = None

    order, created = Order.objects.get_or_create(user=request.user, is_paid=False)
    cart_manager = CartManager(order)

    final_price = option.unit_price * count
    success, message = cart_manager.add_to_cart(service, schedule, final_price, option, count)

    if not success:
        return JsonResponse({
            'status': 'error',
            'message': message,
            'confirm_button_text': 'باشه',
            'icon': 'error',
        })

    return JsonResponse({
        'status': 'success',
        'message': message,
        'confirm_button_text': 'برو به سبد خرید',
        'icon': 'success',
        'url': '/user/cart/'
    })


@login_required
@transaction.atomic
def order_checkout(request: HttpRequest):
    order, _ = Order.objects.get_or_create(is_paid=False, user=request.user)
    order = (
        Order.objects.prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option', 'schedule'))
        )
        .get(pk=order.pk)
    )

    for item in order.items.all():
        if not item.service or (item.schedule and item.schedule.date < date.today()):
            return redirect('user_cart_page')
    if not order.items.exists():
        return redirect('user_cart_page')

    calc = OrderCalculator(order)
    cart_manager = CartManager(order)
    discount_form = DiscountForm(request.POST or None)

    buyer_wallet = request.user.wallet
    wallet_balance = buyer_wallet.balance
    final_price = calc.final_price()
    difference = max(final_price - wallet_balance, 0)

    if request.method == 'POST':
        if 'remove_discount' in request.POST:
            success, message = cart_manager.remove_discount_code(request.user)
            messages.success(request, message) if success else messages.error(request, message)
            return redirect('order_checkout_page')

        elif discount_form.is_valid():
            code = discount_form.cleaned_data['discount_code']
            if code:
                success, message = cart_manager.apply_discount_code(request.user, code)
                messages.success(request, message) if success else messages.error(request, message)
                return redirect('order_checkout_page')

        elif 'pay_with_wallet' in request.POST:
            success, alerts = cart_manager.validate_before_checkout()
            if not success:
                for alert in alerts:
                    messages.error(request, alert['message'])
                return redirect('order_checkout_page')

            if wallet_balance >= final_price:
                with transaction.atomic():
                    for item in order.items.select_related('schedule').all():
                        if item.schedule:
                            schedule = Schedule.objects.select_for_update().get(pk=item.schedule.pk)
                            if schedule.capacity < item.count:
                                messages.error(request, f"ظرفیت برای «{item.service.title}» کافی نیست.")
                                return redirect('user_cart_page')

                            schedule.capacity = F('capacity') - item.count
                            schedule.save(update_fields=['capacity'])

                    freeze_tx = WalletTransaction.create_transaction(
                        wallet=buyer_wallet,
                        type=WalletTransaction.TransactionType.FREEZE,
                        amount=final_price,
                        description=f"خرید سفارش #{order.id} | مبلغ تا تایید فروشنده معلق خواهد بود "
                    )

                    providers_map = {}

                    for item in order.items.all():
                        provider = item.service.provider
                        providers_map.setdefault(provider, []).append(item)
                    for provider, items in providers_map.items():
                        vendor_total = sum(i.final_price for i in items)
                        vendor_order = VendorOrder.objects.create(
                            order=order,
                            provider=provider,
                            total_price=vendor_total,
                            status='pending'
                        )

                        OrderItem.objects.filter(pk__in=[i.pk for i in items]).update(vendor_order=vendor_order)

                        WalletTransaction.objects.create(
                            wallet=provider.user.wallet,
                            related_wallet=buyer_wallet,
                            amount=vendor_total,
                            type=WalletTransaction.TransactionType.FREEZE,
                            description=f"سفارش #{order.id} - VendorOrder #{vendor_order.id}"
                        )

                    order.status = 'pending'
                    order.is_paid = True
                    order.wallet_transaction = freeze_tx
                    order.tracking_code = random.randint(100000, 999999)
                    send_tracking_code_sms(order.user.phone_number, order.tracking_code)
                    notify_user(
                        user=order.user,
                        title='ثبت سفارش',
                        message='سفارش شما با موفقیت ثبت شد و در انتظار تایید فروشنده قرار گرفت.',
                        type_key='order_paid',
                        link=reverse('orders_page'),
                    )
                    order.paid_at = now()
                    order.save()

                request.session['payment_success'] = True
            else:
                messages.error(request, f"موجودی کافی نیست. لطفاً {difference} تومان حساب خود را شارژ کنید.")

    context = {
        'orders': order,
        'discount_form': discount_form,
        'sum': calc.total_price(),
        'discount_amount': calc.discount_amount(),
        'final_price': final_price,
        'wallet_balance': wallet_balance,
        'difference': difference,
        'balance_after': wallet_balance - final_price if wallet_balance >= final_price else wallet_balance,
    }

    if request.session.get('payment_success'):
        context['payment_success'] = True
        del request.session['payment_success']

    return render(request, 'orders/checkout.html', context)


@login_required
@transaction.atomic
def cart_cleanup_view(request: HttpRequest):
    order = Order.objects.filter(user=request.user, is_paid=False).first()
    if not order:
        return JsonResponse([], safe=False)

    cart_manager = CartManager(order)
    alerts, _ = cart_manager.enforce_capacity_constraints()
    return JsonResponse(alerts, safe=False)


@login_required
def remove_cart_item(request):
    base = CartAction(request)
    if not base.order:
        return JsonResponse({'status': 'order_not_found'})

    item_id = base.get_item_id()
    result = base.manager.remove_item(item_id)
    return base.render_response(result)


@login_required
def clear_cart_items(request):
    base = CartAction(request)
    if not base.order:
        return JsonResponse({'status': 'orders_not_found'})

    result = base.manager.clear_cart()
    return base.render_response(result)


@login_required
def change_cart_item_count(request):
    base = CartAction(request)
    if not base.order:
        return JsonResponse({'status': 'order_not_found'})

    item_id = base.get_item_id()
    state = request.GET.get('state')
    if not item_id or not state:
        return JsonResponse({'status': 'invalid_data'})

    result = base.manager.change_item_count(item_id, state)
    if result.get('status') != 'success':
        return JsonResponse(result)
    return base.render_response(result)


@login_required
def update_cart_data(request):
    order = Order.objects.filter(user=request.user, is_paid=False).first()
    if not order:
        return JsonResponse({'status': 'order_not_found'})

    code = request.GET.get('discount_code')
    manager = CartManager(order)
    data = manager.update_cart_data(request.user, code)
    return JsonResponse(data)
