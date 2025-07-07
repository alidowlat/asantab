from datetime import date
from django.db import transaction
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.templatetags.extra_filters import rounded
from discounts.models import DiscountCode, DiscountCodeUser
from orders.models import OrderItem, Order
from orders.services import OrderCalculator
from services.models import Reservation


class CartManager:
    def __init__(self, order):
        self.order = order

    def _is_schedule_available(self, schedule):
        return not Reservation.objects.filter(schedule=schedule).exists()

    def _create_reserve(self, user, provider, schedule, option):
        return Reservation.objects.create(
            user=user,
            provider=provider,
            service=option.service,
            option=option,
            schedule=schedule,
            status='pending',
        )

    @transaction.atomic
    def add_to_cart(self, service, schedule, final_price, option, count):
        if schedule.date < date.today():
            return False, "نمی‌توان زمان رزرو گذشته را انتخاب کرد."

        if not self._is_schedule_available(schedule):
            return False, "زمان‌بندی انتخاب‌شده قبلاً رزرو شده است."

        item = OrderItem.objects.filter(
            order=self.order,
            option=option,
        ).first()

        if item:
            item.count += count
            item.final_price = final_price * item.count
            item.save()
        else:
            OrderItem.objects.create(
                order=self.order,
                service=service,
                schedule=schedule,
                option=option,
                count=count,
                final_price=final_price,
            )

        calculator = OrderCalculator(self.order)
        self.order.final_price = calculator.final_price()
        self.order.save()

        return True, "آیتم با موفقیت به سبد خرید افزوده شد."

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

    def clear_cart(self):
        if not self.order:
            return {'status': 'items_not_found', 'message': 'سفارشی یافت نشد.'}

        has_items = self.order.items.exists()
        self.order.delete()

        return {
            'status': 'success',
            'order_deleted': True,
            'message': 'سفارش از سبد خرید حذف شد.' if has_items else 'سبد خرید خالی بود.'
        }

    def change_item_count(self, item_id, state):
        item = self.order.items.select_related('option', 'schedule').filter(id=item_id).first()

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
            unit_price = item.option.unit_price
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
            'total_discount': rounded(calc.discount_amount()),
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

    def remove_discount_code(self, user):
        if not self.order.discount_code:
            return False, "کدی برای حذف وجود ندارد."
        DiscountCodeUser.objects.filter(user=user, discount_code=self.order.discount_code).delete()
        self.order.discount_code = None
        self.order.save()
        return True, "کد تخفیف حذف شد."


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

        if result.get('order_deleted') or not self.order.items.exists():
            body = render_to_string('orders/cart_content.html', {'orders': None, 'sum': 0})
        else:
            calc = OrderCalculator(self.order)
            body = render_to_string('orders/cart_content.html', {
                'orders': self.order,
                'sum': calc.total_price(),
                'discount_amount': calc.discount_amount(),
                'final_price': calc.final_price(),
            })

        return JsonResponse({**result, 'body': body})
