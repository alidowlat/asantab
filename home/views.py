from django.db.models import Prefetch
from django.views.generic import TemplateView
from django.shortcuts import render

from config.models import SiteSetting, FooterBox, SocialLink, MainCategory, CategoryItem
from services.models import Service, Platform, Favorite


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
    platforms = Platform.objects.all().prefetch_related(
        Prefetch('main_categories', queryset=MainCategory.objects.prefetch_related('category_items').order_by('order'))
    )
    if request.user.is_authenticated:
        favorite_list = Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
    else:
        favorite_list = []

    context = {
        'site_settings': site_settings,
        'platforms': platforms,
        'favorite_list': favorite_list,
    }
    return render(request, 'shared/header_comp.html', context)



def site_footer_component(request):
    site_settings = SiteSetting.objects.get(is_main=True)
    footer_boxes = FooterBox.objects.prefetch_related('footer_links').all()
    social_links = SocialLink.objects.prefetch_related('site_setting').all()

    context = {
        'site_settings': site_settings,
        'footer_boxes': footer_boxes,
        'social_links': social_links,
    }
    return render(request, 'shared/footer_comp.html', context)


def about_us(request):
    return render(request, 'home/about.html')


def error_404(request, exception):
    return render(request, 'home/404.html', {})
