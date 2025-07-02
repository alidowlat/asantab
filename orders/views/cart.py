from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from orders.forms import DiscountForm
from orders.models import Order, OrderItem
from orders.services import OrderCalculator
from orders.services.cart_service import CartManager, CartAction
from services.models import Option, Schedule, Service


@login_required
def user_cart(request: HttpRequest):
    current_order, created = Order.objects.prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option', 'schedule'))
    ).get_or_create(is_paid=False, user=request.user)
    calc = OrderCalculator(current_order)

    context = {
        'orders': current_order,
        'sum': calc.total_price(),
        'discount_amount': calc.discount_amount(),
        'final_price': calc.final_price(),
    }
    return render(request, 'orders/cart.html', context)


@login_required
def add_service_to_cart(request):
    service_id = request.GET.get('service_id')
    option_id = request.GET.get('option_id')
    count = int(request.GET.get('count', 1))
    schedule_id = int(request.GET.get('schedule_id'))

    if count < 1:
        return JsonResponse({'status': 'invalid_count', 'message': 'تعداد معتبر نیست'})

    service = Service.objects.filter(id=service_id).first()
    option = Option.objects.filter(id=option_id).first()
    schedule = Schedule.objects.filter(id=schedule_id).first()

    if not service or not option or not schedule:
        return JsonResponse({'status': 'not_found', 'message': 'پارامترهای ورودی نامعتبر است'})

    order, created = Order.objects.get_or_create(user=request.user, is_paid=False)

    cart_manager = CartManager(order)

    final_price = option.unit_price * count

    cart_manager.add_to_cart(service, schedule, final_price, option, count)

    return JsonResponse({'status': 'success', 'message': 'خدمت به سبد اضافه شد'})


@login_required
def order_checkout(request: HttpRequest):
    order, created = Order.objects.get_or_create(is_paid=False, user=request.user)
    order = Order.objects.prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option', 'schedule'))
    ).get(pk=order.pk)

    if not order.items.exists():
        return redirect('user_cart_page')

    calc = OrderCalculator(order)
    cart_manager = CartManager(order)
    discount_form = DiscountForm(request.POST or None)

    if request.method == 'POST':
        if 'remove_discount' in request.POST:
            success, message = cart_manager.remove_discount_code(request.user)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('order_checkout_page')

        elif discount_form.is_valid():
            code = discount_form.cleaned_data['discount_code']
            if code:
                success, message = cart_manager.apply_discount_code(request.user, code)
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)
                return redirect('order_checkout_page')

    context = {
        'orders': order,
        'discount_form': discount_form,
        'sum': calc.total_price(),
        'discount_amount': calc.discount_amount(),
        'final_price': calc.final_price(),
    }
    return render(request, 'orders/checkout.html', context)


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
