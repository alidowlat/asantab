from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max, Min, Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from config.views import apply_filters
from locations.models import City
from services.models import Service, Category, Profession, ServiceTag, Platform


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

        all_prices = []

        for service in context['services']:
            prices = list(service.options.filter(unit_price__isnull=False).values_list('unit_price', flat=True))
            service.min_price = min(prices) if prices else None
            service.max_price = max(prices) if prices else None
            all_prices.extend(prices)

        global_min_price = min(all_prices) if all_prices else 0
        global_max_price = max(all_prices) if all_prices else 0

        context['global_min_price'] = global_min_price
        context['global_max_price'] = global_max_price

        model_fields = [
            ('platforms', Platform.objects.all()),
            ('categories', Category.objects.filter(is_active=True)),
            ('professions', Profession.objects.all()),
            ('tags', ServiceTag.objects.all()),
            ('locations', City.objects.filter(services__is_active=True).distinct())
        ]

        for field_name, queryset in model_fields:
            context[field_name] = queryset

        return context

    def get_queryset(self):
        base_qs = Service.objects.annotate(
            min_price=Min('options__unit_price'),
            max_price=Max('options__unit_price'),
            visit_count=Count('visits', distinct=True),
        ).filter(min_price__isnull=False)

        filtered_qs = apply_filters(self.request, base_qs)

        sort_by = self.request.GET.get('sort_by')
        match sort_by:
            case 'most_expensive':
                filtered_qs = filtered_qs.order_by('-max_price', '-id')
            case 'most_viewed':
                filtered_qs = filtered_qs.order_by('-visit_count', '-id')
            case 'cheapest':
                filtered_qs = filtered_qs.order_by('min_price', '-id')
            case 'newest':
                filtered_qs = filtered_qs.order_by('-id')

        return filtered_qs


@staff_member_required
@require_POST
def toggle_unique_status(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_unique = not service.is_unique
    service.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
