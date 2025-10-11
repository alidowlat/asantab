from itertools import zip_longest

from django.db.models import Prefetch, Count, F, Sum
from django.db.models.functions import Lower
from django.views.generic import TemplateView
from django.shortcuts import render
from blog.models import Post
from config.models import SiteSetting, FooterBox, SocialLink, MainCategory
from notifications.models import Notification
from orders.models import Order, OrderItem
from search.models import SearchQuery
from services.models import Service, Platform, Favorite


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def chunked(self, iterable, n):
        args = [iter(iterable)] * n
        return [list(filter(None, group)) for group in zip_longest(*args)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        model_fields = [
            ('featured_services',
             Service.objects.filter(is_unique=True, is_active=True, status='approved').order_by('-id')[:5]),

            ('newest_services',
             Service.objects.filter(is_active=True, status='approved').order_by('-id')[:10]),

            ('most_viewed_services',
             Service.objects.annotate(
                 visit_count=Count('visits', distinct=True)
             ).filter(is_active=True, status='approved').order_by('-visit_count', '-id')[:10]),

            ('most_sold_services',
             Service.objects.annotate(
                 total_sold=Sum('orderitem__count')
             ).filter(is_active=True, status='approved', total_sold__gt=0).order_by('-total_sold', '-id')[:12]),

            ('blog',
             Post.objects.filter(is_active=True).order_by('-created_at')[:8]),
        ]

        for field_name, queryset in model_fields:
            context[field_name] = queryset

        context['most_sold_chunks'] = self.chunked(context['most_sold_services'], 3)

        return context


def site_header_component(request):
    site_settings = SiteSetting.objects.get(is_main=True)
    platforms = Platform.objects.all().prefetch_related(
        Prefetch('main_categories', queryset=MainCategory.objects.prefetch_related('category_items').order_by('order'))
    )

    if request.user.is_authenticated:
        favorite_list = Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
        notif_list = Notification.objects.filter(user=request.user).order_by('-created_at')
        order = Order.objects.filter(user=request.user, is_paid=False).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option', 'schedule'))
        ).first()
    else:
        favorite_list = []
        notif_list = []
        order = []

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
        'orders': order,
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
