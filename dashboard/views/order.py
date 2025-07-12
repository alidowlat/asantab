from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.views.generic import ListView
from orders.models import Order, OrderItem
from orders.services import OrderCalculator


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/order/main.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)

        def get_orders(is_paid, select_fields=None):
            queryset = Order.objects.filter(user=self.request.user, is_paid=is_paid)
            if select_fields:
                queryset = queryset.prefetch_related(
                    Prefetch('items', queryset=OrderItem.objects.select_related(*select_fields))
                )
            else:
                queryset = queryset.prefetch_related('items')
            return queryset


        cart_items = get_orders(False, ['service', 'option', 'schedule'])
        order_items = get_orders(True, ['service'])

        context['cart_items'] = cart_items
        context['order_items'] = order_items
        context['final_price'] = sum(OrderCalculator(order).final_price() for order in order_items)

        return context
