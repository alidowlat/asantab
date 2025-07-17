from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from accounts.models import Provider
from accounts.services import calculate_profile_completion
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
        calc = OrderCalculator(latest_orders[0]) if latest_orders else None

        context.update({
            'user': user,
            'orders': latest_orders,
            'user_notifs': Notification.objects.filter(user=user, is_read=False),
            'final_price': calc.final_price() if calc else 0,
            'current_orders_count': all_orders.filter(status__in=['pending', 'accepted']).count(),
            'completed_orders_count': all_orders.filter(status='completed').count(),
            'canceled_orders_count': all_orders.filter(status='rejected').count(),
        })

        return context


def get_progress_color(percent):
    if percent < 20:
        return "red-500"
    elif percent < 80:
        return "yellow-500"
    else:
        return "success"


@login_required
def dashboard_menu(request):
    if request.user.is_provider:
        provider = Provider.objects.get(user=request.user)
    else:
        provider = None

    if provider:
        completion_percent = calculate_profile_completion(provider)
        progress_color = get_progress_color(completion_percent)
    else:
        completion_percent = 0
        progress_color = "gray-400"

    return render(request, 'dashboard/sidebar/_menu.html', {
        'completion_percent': completion_percent,
        'progress_color': progress_color
    })
