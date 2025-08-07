from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max, Min, Count
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from accounts.models import Provider
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


class ProviderListView(ListView):
    model = Provider
    template_name = "providers/list.html"
    context_object_name = 'providers'
    paginate_by = 12

    def get_queryset(self):
        return Provider.objects.select_related("user").order_by("-id")


@staff_member_required
@require_POST
def toggle_unique_status(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_unique = not service.is_unique
    service.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
