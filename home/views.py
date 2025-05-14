from django.views.generic import TemplateView
from django.shortcuts import render

from config.models import SiteSetting, FooterBox
from services.models import Service


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        request = self.request

        featured_services = Service.objects.filter(is_unique=True, is_active=True, status='approved').order_by('-id')[:5]
        context['featured_services'] = featured_services

        newest_services = Service.objects.filter(is_active=True, status='approved').order_by('-id')[:10]
        context['newest_services'] = newest_services

        return context


def site_header_component(request):
    site_settings = SiteSetting.objects.get(is_main=True)

    context = {
        'site_settings': site_settings,
    }
    return render(request, 'shared/header_comp.html', context)


def site_footer_component(request):
    site_settings = SiteSetting.objects.get(is_main=True)
    footer_boxes = FooterBox.objects.prefetch_related('footerlink_set').all()

    context = {
        'site_settings': site_settings,
        'footer_boxes': footer_boxes,
    }
    return render(request, 'shared/footer_comp.html', context)


def about_us(request):
    return render(request, 'home/about.html')


def error_404(request, exception):
    return render(request, 'home/404.html', {})
