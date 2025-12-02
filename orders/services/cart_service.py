from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.templatetags.extra_filters import rounded
from discounts.models import DiscountCode, DiscountCodeUser
from orders.models import OrderItem, Order
from orders.services import OrderCalculator
from services.models import Reservation, Schedule, Service, Option


class CartManager:
    def __init__(self, order):
        self.order = order

    def _reserved_count_for_schedule(self, schedule: Schedule) -> int:
        reserved = OrderItem.objects.filter(
            Q(schedule=schedule) &
            Q(order__is_paid=True) &
            Q(vendor_order__status__in=['accepted'])
        ).aggregate(total=Sum('count'))['total'] or 0
        return int(reserved)

    def _remaining_capacity(self, schedule):
        if schedule is None:
            return 0
        return max(0, schedule.capacity or 0)

    def _recalculate_order(self):
        # محاسبه‌ی دوباره قیمت نهایی و ذخیره‌ی آن (اگر order ممکنه None باشه کنترل کن)
        if not self.order:
            return
        calc = OrderCalculator(self.order)
        # اگر Order مدل property final_price داره که readonly هست، از فیلد DB واقعی استفاده کن
        # من فرض میکنم order.final_price قابل ست است اگر نه: ذخیره در یک فیلد دیگر (مثلاً order.cached_final_price)
        try:
            self.order.final_price = calc.final_price()
            self.order.save(update_fields=['final_price'])
        except Exception:
            # fallback: save all
            self.order.save()

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
    def validate_before_checkout(self):
        """
        بررسی نهایی سبد قبل از شروع پرداخت.
        - enforce_capacity_constraints اجرا می‌شود
        - اگر آیتمی حذف یا تغییر داده شد، پیام مناسب برمی‌گرداند
        خروجی: (success, alerts)
        """
        alerts, order = self.enforce_capacity_constraints()

        if not order:
            return False, alerts  # یعنی کل سفارش حذف شده

        if alerts:
            return False, alerts  # یعنی تغییراتی رخ داده

        return True, []

    @transaction.atomic
    def add_to_cart(self, service: Service, schedule: Schedule, final_price: Decimal, option: Option, count: int):
        if count < 1:
            return False, "تعداد معتبر نیست."

        if schedule:
            if schedule.date and schedule.date < date.today():
                return False, "نمی‌توان زمان رزرو گذشته را انتخاب کرد."

            schedule = Schedule.objects.select_for_update().get(pk=schedule.pk)
            remaining_capacity = self._remaining_capacity(schedule)
            if remaining_capacity <= 0:
                return False, "ظرفیت این زمان پر شده است."
            if count > remaining_capacity:
                return False, f"حداکثر ظرفیت باقی‌مانده {remaining_capacity} عدد است."
        else:
            remaining_capacity = None

        item = OrderItem.objects.select_for_update().filter(
            order=self.order,
            option=option,
            schedule=schedule,
        ).first()

        if item:
            new_count = item.count + count
            if remaining_capacity is not None:
                if new_count > remaining_capacity:
                    item.count = remaining_capacity
                    item.final_price = item.count * option.unit_price
                    item.save(update_fields=['count', 'final_price'])
                    self._recalculate_order()
                    return False, f"تعداد به حداکثر ظرفیت ({remaining_capacity}) محدود شد."
                item.count = new_count
                item.final_price = item.count * option.unit_price
                item.save(update_fields=['count', 'final_price'])
        else:
            OrderItem.objects.create(
                order=self.order,
                service=service,
                schedule=schedule,
                option=option,
                count=count,
                final_price=count * option.unit_price,
            )

        self._recalculate_order()

        return True, "آیتم با موفقیت به سبد خرید افزوده شد."

    def cleanup_order_if_invalid(self):
        for item in self.order.items.select_related('schedule'):
            if not item.service:
                item.delete()
                continue

            if item.schedule:
                if item.schedule.date < date.today():
                    item.delete()
                    continue

                remaining_capacity = self._remaining_capacity(item.schedule)
                if remaining_capacity <= 0:
                    item.delete()
                    continue
                elif item.count > remaining_capacity:
                    item.count = remaining_capacity
                    item.final_price = item.count * item.option.unit_price
                    item.save()

        if not self.order.items.exists():
            if self.order.discount_code:
                DiscountCodeUser.objects.filter(
                    user=self.order.user, discount_code=self.order.discount_code
                ).delete()
            self.order.delete()
            return None

        return self.order

    @transaction.atomic
    def enforce_capacity_constraints(self):
        """
        بررسی تمام آیتم‌های سبد و:
         - حذف آیتم‌هایی که دیگر ظرفیت ندارند
         - کاهش تعداد آیتم‌هایی که بیشتر از ظرفیت شده‌اند
        برمی‌گرداند لیست alertها (هر alert یک دیکت با keys: type, message).
        """
        alerts = []

        # iterate items with schedule
        for item in list(self.order.items.select_related('schedule', 'option', 'service')):
            if not item.schedule:
                continue

            # lock schedule row
            schedule = Schedule.objects.select_for_update().get(pk=item.schedule.pk)
            remaining = self._remaining_capacity(schedule)

            if remaining <= 0:
                alerts.append({'type': 'error', 'message': f'ظرفیت «{item.service.title}» پر شده و از سبد حذف شد.'})
                item.delete()
                continue

            if item.count > remaining:
                # کاهش تعداد و ذخیره
                item.count = remaining
                item.final_price = item.count * (item.option.unit_price if item.option else 0)
                item.save(update_fields=['count', 'final_price'])
                alerts.append(
                    {'type': 'warning', 'message': f'تعداد «{item.service.title}» بیشتر از ظرفیت بود. به {remaining} کاهش یافت.'})

        # اگر آیتمی نمانده، پاکسازی کلی انجام بده
        if not self.order.items.exists():
            if self.order.discount_code:
                DiscountCodeUser.objects.filter(user=self.order.user, discount_code=self.order.discount_code).delete()
            self.order.delete()
            return alerts, None

        # recalc final price
        self._recalculate_order()
        return alerts, self.order

    def remove_item(self, item_id: int):
        try:
            item = self.order.items.get(id=item_id)
        except OrderItem.DoesNotExist:
            return {'status': 'item_not_found', 'message': 'آیتم یافت نشد.'}
        item.delete()
        if not self.order.items.exists():
            if self.order.discount_code:
                DiscountCodeUser.objects.filter(user=self.order.user, discount_code=self.order.discount_code).delete()
            self.order.delete()
            return {'status': 'success', 'order_deleted': True, 'message': 'سفارش حذف شد چون آیتمی باقی نماند.'}
        self._recalculate_order()
        return {'status': 'success', 'order_deleted': False, 'message': 'آیتم از سبد خرید حذف شد.'}

    def clear_cart(self):
        if not self.order:
            return {'status': 'items_not_found', 'message': 'سفارشی یافت نشد.'}
        has_items = self.order.items.exists()
        self.order.delete()
        return {'status': 'success', 'order_deleted': True,
                'message': 'سفارش از سبد خرید حذف شد.' if has_items else 'سبد خرید خالی بود.'}

    @transaction.atomic
    def change_item_count(self, item_id: int, state: str):
        """
        افزایش/کاهش تعداد آیتم (state = 'increase' | 'decrease').
        برمی‌گرداند dictionary که وضعیت و پیام را دارد.
        """
        item = self.order.items.select_related('option', 'schedule').filter(id=item_id).first()
        if not item:
            return {'status': 'item_not_found', 'message': 'آیتم یافت نشد.'}

        # اگر schedule دارد، قفل و چک ظرفیت
        if item.schedule:
            schedule = Schedule.objects.select_for_update().get(pk=item.schedule.pk)
            remaining_capacity = self._remaining_capacity(schedule)
        else:
            remaining_capacity = None

        if state == 'increase':
            if item.schedule and (item.count + 1) > remaining_capacity:
                return {'status': 'error', 'message': f"حداکثر ظرفیت باقی‌مانده {remaining_capacity} عدد است."}
            item.count += 1
        elif state == 'decrease':
            if item.count <= 1:
                # حذف آیتم
                item.delete()
                # اگر سفارشی نماند، حذف order و پاکسازی کدتخفیف
                if not self.order.items.exists():
                    if self.order.discount_code:
                        DiscountCodeUser.objects.filter(user=self.order.user, discount_code=self.order.discount_code).delete()
                    self.order.delete()
                    return {'status': 'success', 'order_deleted': True}
                # recalc
                self._recalculate_order()
                return {'status': 'success', 'order_deleted': False}
            item.count -= 1
        else:
            return {'status': 'state_invalid', 'message': 'عملیات نامعتبر.'}

        # update price
        try:
            unit_price = item.option.unit_price
        except Exception:
            return {'status': 'invalid_item_price', 'message': 'قیمت واحد آیتم معتبر نیست.'}

        item.final_price = item.count * unit_price
        item.save(update_fields=['count', 'final_price'])

        # recalc order
        self._recalculate_order()

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
            'discount_code': self.order.discount_code.code,
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
