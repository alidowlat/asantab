from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max, Min, Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from locations.models import City
from services.models import Service, Category, Profession, Tag, Platform


class ServiceListView(ListView):
    template_name = 'services/list.html'
    model = Service
    context_object_name = 'services'
    ordering = ['-id']
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        latest_service = self.object_list.first()
        context['latest_service'] = latest_service

        for service in context['services']:
            prices = list(service.options.filter(unit_price__isnull=False).values_list('unit_price', flat=True))
            service.min_price = min(prices) if prices else None
            service.max_price = max(prices) if prices else None

        model_fields = [
            ('platforms', Platform.objects.all()),
            ('categories', Category.objects.filter(is_active=True)),
            ('professions', Profession.objects.all()),
            ('tags', Tag.objects.all()),
            ('locations', City.objects.filter(services__is_active=True).distinct())
        ]

        for field_name, queryset in model_fields:
            context[field_name] = queryset

        return context

    def get_queryset(self):
        request = self.request
        sort_by = request.GET.get('sort_by')
        platform = request.GET.get('platform')
        category = request.GET.get('category')
        profession = request.GET.get('profession')
        location = request.GET.get('location')
        tag = request.GET.get('tag')
        available = request.GET.get('available')
        featured = request.GET.get('featured')
        search = request.GET.get('s')

        query = Service.objects.annotate(
            min_price=Min('options__unit_price'),
            max_price=Max('options__unit_price'),
            visit_count=Count('visits', distinct=True),
        ).filter(min_price__isnull=False)

        if platform:
            query = query.filter(platform__slug__in=platform.split(','))

        if category:
            query = query.filter(category__slug__in=category.split(','))

        if profession:
            query = query.filter(profession__slug__in=profession.split(','))

        if location:
            query = query.filter(locations__name_en__in=location.split(','))

        if tag:
            query = query.filter(tags__slug__in=tag.split(','))

        if available == '1':
            query = query.filter(is_active=True)

        if featured == '1':
            query = query.filter(is_unique=True)

        if search:
            query = query.filter(title__icontains=search)

        match sort_by:
            case 'most_expensive':
                query = query.order_by('-max_price', '-id')
            case 'most_viewed':
                query = query.order_by('-visit_count', '-id')
            case 'cheapest':
                query = query.order_by('min_price', '-id')
            case 'newest':
                query = query.order_by('-id')

        return query


@staff_member_required
@require_POST
def toggle_unique_status(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_unique = not service.is_unique
    service.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
