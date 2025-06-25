from django.db.models import Prefetch, Count, F
from django.db.models.functions import Lower
from django.views.generic import TemplateView
from django.shortcuts import render
from blog.models import Post
from config.models import SiteSetting, FooterBox, SocialLink, MainCategory
from notifications.models import Notification
from search.models import SearchQuery
from services.models import Service, Platform, Favorite


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        request = self.request

        model_fields = [
            ('featured_services', Service.objects.filter(is_unique=True, is_active=True, status='approved').order_by('-id')[:5]),
            ('newest_services', Service.objects.filter(is_active=True, status='approved').order_by('-id')[:10]),
            ('blog', Post.objects.filter(is_active=True).order_by('-created_at')[:8]),
        ]

        for field_name, queryset in model_fields:
            context[field_name] = queryset

        return context


def site_header_component(request):
    site_settings = SiteSetting.objects.get(is_main=True)
    platforms = Platform.objects.all().prefetch_related(
        Prefetch('main_categories', queryset=MainCategory.objects.prefetch_related('category_items').order_by('order'))
    )
    if request.user.is_authenticated:
        favorite_list = Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
        notif_list = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        favorite_list = []
        notif_list = []

    popular_search = list(
        SearchQuery.objects
        .annotate(query_lower=Lower('query'))
        .values(name=F('query_lower'))
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    if request.user.is_authenticated:
        raw_queries = SearchQuery.objects.filter(user_id=request.user.id).order_by('-created_at').values_list('query', flat=True)

        seen = set()
        search_history = []
        for q in raw_queries:
            cleaned = q.strip().lower()
            if cleaned not in seen:
                seen.add(cleaned)
                search_history.append(q.strip())
            if len(search_history) >= 10:
                break
    else:
        search_history = []

    context = {
        'site_settings': site_settings,
        'platforms': platforms,
        'favorite_list': favorite_list,
        'notif_list': notif_list,
        'search_history': search_history,
        'popular_search': popular_search,
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
