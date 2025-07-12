from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from accounts.models import Provider
from notifications.models import Notification
from orders.models import OrderItem, Order
from orders.services import OrderCalculator


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_provider:
            context['provider'] = get_object_or_404(Provider, user=user)

        all_orders = Order.objects.filter(user=user, is_paid=True).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('service'))
        ).order_by('-id')

        latest_orders = list(all_orders[:3])

        current_orders_count = all_orders.filter(status__in=['pending', 'accepted']).count()
        completed_orders_count = all_orders.filter(status='completed').count()
        canceled_orders_count = all_orders.filter(status='rejected').count()

        calc = OrderCalculator(latest_orders[0]) if latest_orders else None

        context.update({
            'user': user,
            'orders': latest_orders,
            'user_notifs': Notification.objects.filter(user=user, is_read=False),
            'final_price': calc.final_price() if calc else 0,
            'current_orders_count': current_orders_count,
            'completed_orders_count': completed_orders_count,
            'canceled_orders_count': canceled_orders_count,
        })

        return context

