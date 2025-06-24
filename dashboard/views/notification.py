from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView
from notifications.models import Notification


class NotificationsView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/notification/main.html'
    context_object_name = 'notifications'
    model = Notification

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related('notif_type').order_by('-created_at')


@login_required
def dashboard_notifications_partial(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/notification/list.html', {'notifications': notifications})
