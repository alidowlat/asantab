from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from accounts.models import Provider


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        request = self.request
        user = request.user
        if user.is_provider:
            provider = get_object_or_404(Provider, user=user)
            context['provider'] = provider

        context['user'] = user

        return context
