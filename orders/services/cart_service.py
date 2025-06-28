from datetime import date
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.templatetags.extra_filters import rounded
from discounts.models import DiscountCode, DiscountCodeUser
from orders.models import OrderItem, Order
from orders.services import OrderCalculator


class CartManager:
    def __init__(self, order):
        self.order = order

    def remove_item(self, item_id):
        try:
            item = self.order.items.get(id=item_id)
        except OrderItem.DoesNotExist:
            return {'status': 'item_not_found', 'message': 'آیتم یافت نشد.'}

        item.delete()

        if not self.order.items.exists():
            self.order.delete()
            return {
                'status': 'success',
                'order_deleted': True,
                'message': 'سفارش حذف شد چون آیتمی باقی نماند.'
            }

        return {
            'status': 'success',
            'order_deleted': False,
            'message': 'آیتم از سبد خرید حذف شد.'
        }

    def change_item_count(self, item_id, state):
        item = self.order.items.select_related('service__options').filter(id=item_id).first()
        if not item:
            return {'status': 'item_not_found'}

        if state == 'increase':
            item.count += 1
        elif state == 'decrease':
            if item.count == 1:
                item.delete()
                if not self.order.items.exists():
                    self.order.delete()
                    return {'status': 'success', 'order_deleted': True}
                return {'status': 'success', 'order_deleted': False}
            item.count -= 1
        else:
            return {'status': 'state_invalid'}

        try:
            unit_price = item.service.options.unit_price
        except AttributeError:
            return {'status': 'invalid_item_price'}

        item.final_price = item.count * unit_price
        item.save()

        return {'status': 'success', 'order_deleted': False}

    def update_cart_data(self, user, code=None):
        calc = OrderCalculator(self.order)

        if code:
            success, _ = self.apply_discount_code(user, code)
            if success:
                calc = OrderCalculator(self.order)

        return {
            'total_price': rounded(calc.total_price()),
            'total_discount': rounded(calc.total_discount()),
            'final_price': rounded(calc.final_price()),
            'discount_code': rounded(calc.discount_amount())
        }

    def apply_discount_code(self, user, code):
        discount = DiscountCode.objects.filter(code=code, expiration_date__gte=date.today()).first()

        if not discount:
            return False, "کد تخفیف اشتباه یا منقضی شده است."

        if DiscountCodeUser.objects.filter(user=user, discount_code=discount).exists():
            return False, "کد تخفیف قبلا استفاده شده است."

        DiscountCodeUser.objects.create(user=user, discount_code=discount)
        self.order.discount_code = discount
        self.order.save()
        return True, "کد تخفیف اعمال شد."

class CartAction:
    def __init__(self, request):
        self.request = request
        self.order = Order.objects.filter(user=request.user, is_paid=False).first()
        self.manager = CartManager(self.order) if self.order else None

    def get_item_id(self):
        return self.request.GET.get('item_id')

    def render_response(self, result):
        if not self.order or not self.manager:
            return JsonResponse({'status': 'order_not_found'})

        if result.get('order_deleted'):
            body = render_to_string('orders/cart_content.html', {'order': None, 'sum': 0})
        else:
            calc = OrderCalculator(self.order)
            body = render_to_string('orders/cart_content.html', {
                'order': self.order,
                'sum': calc.total_price(),
            })

        return JsonResponse({**result, 'body': body})