from django.views.generic import TemplateView
from django.shortcuts import render

from services.models import Service


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        request = self.request

        featured_services = Service.objects.filter(is_unique=True, is_active=True, status='approved')[:8]
        context['featured_services'] = featured_services

        return context


def site_header_component(request):
    return render(request, 'shared/header_comp.html')


def site_footer_component(request):
    return render(request, 'shared/footer_comp.html')


def about_us(request):
    return render(request, 'home/about.html')


def error_404(request, exception):
    return render(request, 'home/404.html', {})
