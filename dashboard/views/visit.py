from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView
from services.models import Visit


class VisitListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/visit/main.html'
    context_object_name = 'visit_list'
    model = Visit

    def get_context_data(self, **kwargs):
        context = super(VisitListView, self).get_context_data(**kwargs)
        request = self.request
        context['visit_list'] = (
            Visit.objects.filter(user=request.user).select_related('service').order_by('-created_at')
        )

        return context


def dashboard_visit_list_partial(LoginRequiredMixin, request):
    visit_list = Visit.objects.filter(user=request.user).select_related('service').order_by('-created_at')
    return render(request, 'dashboard/visit/list.html', {'visit_list': visit_list})