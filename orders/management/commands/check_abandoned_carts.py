from django.core.management.base import BaseCommand
from notifications.services import notify_user
from django.utils import timezone
from orders.models import Order
from datetime import timedelta


class Command(BaseCommand):
    help = 'Check for abandoned carts and notify users'

    def handle(self, *args, **kwargs):
        cutoff_time = timezone.now() - timedelta(days=1)
        abandoned_orders = Order.objects.filter(
            is_paid=False,
            updated_at__lt=cutoff_time
        )

        for order in abandoned_orders:
            notify_user(
                user=order.user,
                title="سبد خریدت منتظرته!",
                message="یه روز گذشته و هنوز سفارشتو کامل نکردی. بیا ادامه بده :)",
                type_key="abandoned_cart",
                link="/orders/cart"
            )

        self.stdout.write(self.style.SUCCESS(f"check's done, {abandoned_orders.count()} cart is abandoned."))
