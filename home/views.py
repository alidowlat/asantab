from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home/index.html'


def site_header_component(request):
    return render(request, 'shared/header_comp.html')


def site_footer_component(request):
    return render(request, 'shared/footer_comp.html')


def about_us(request):
    return render(request, 'home/about.html')


def error_404(request, exception):
    return render(request, 'home/404.html', {})
