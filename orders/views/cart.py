from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from orders.forms import DiscountForm
from orders.models import Order, OrderItem
from orders.services import OrderCalculator
from orders.services.cart_service import CartManager, CartAction


@login_required
def user_cart(request: HttpRequest):
    current_order, created = Order.objects.prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option'))
    ).get_or_create(is_paid=False, user=request.user)

    calc = OrderCalculator(current_order)
    cart_manager = CartManager(current_order)
    discount_form = DiscountForm(request.POST or None)

    if request.method == 'POST' and discount_form.is_valid():
        code = discount_form.cleaned_data['discount_code']
        if code:
            success, message = cart_manager.apply_discount_code(request.user, code)
            messages.info(request, message)
            return redirect('user_cart_page')

    context = {
        'orders': current_order,
        'discount_form': discount_form,
        'sum': calc.total_price(),
        'discount_amount': calc.discount_amount(),
        'final_price': calc.final_price(),
    }
    return render(request, 'orders/cart.html', context)


@login_required
def remove_cart_item(request):
    base = CartAction(request)
    if not base.order:
        return JsonResponse({'status': 'order_not_found'})

    item_id = base.get_item_id()
    result = base.manager.remove_item(item_id)
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
