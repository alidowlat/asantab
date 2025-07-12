from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.views.generic import ListView, DetailView
from orders.models import Order, OrderItem
from orders.services import OrderCalculator
from orders.models import STATUS_CHOICES


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/order/main.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)

        def get_orders(is_paid, select_fields=None, status=None):
            queryset = Order.objects.filter(user=self.request.user, is_paid=is_paid)
            if status:
                queryset = queryset.filter(status=status)
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

        for status_value, _ in STATUS_CHOICES:
            context[f'order_{status_value}'] = get_orders(True, ['service'], status_value)

        context['final_price'] = sum(OrderCalculator(order).final_price() for order in order_items)

        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/order/order_detail.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        loaded_order = Order.objects.filter(user=self.request.user, is_paid=True).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option', 'schedule'))
        ).first()
        order = Order.objects.filter(user=self.request.user, is_paid=True)
        calc = OrderCalculator(loaded_order) if loaded_order else None

        context['discount_amount'] = calc.discount_amount() if calc else 0
        context['loaded_order'] = loaded_order
        context['final_price'] = sum(OrderCalculator(order).final_price() for order in order)

        return context
