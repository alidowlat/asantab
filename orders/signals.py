from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import VendorOrder


@receiver(post_save, sender=VendorOrder)
def update_order_status_based_on_vendors(sender, instance, **kwargs):
    order = instance.order

    if order.vendor_orders.exists() and not order.vendor_orders.exclude(status="accepted").exists():
        if order.status != "accepted":
            order.status = "accepted"
            order.save(update_fields=["status"])
        return

    if order.vendor_orders.exists() and not order.vendor_orders.exclude(status="completed").exists():
        if order.status != "completed":
            order.status = "completed"
            order.save(update_fields=["status"])
        return