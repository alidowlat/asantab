from django.db.models import Q
from django.views.generic import DetailView
from services.models import Service


class ServiceDetailView(DetailView):
    template_name = 'services/detail.html'
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_service = self.object

        prices = list(loaded_service.options.filter(unit_price__isnull=False).values_list('unit_price', flat=True))
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        context['min_price'] = min_price
        context['max_price'] = max_price

        related_services = Service.objects.filter(
            Q(profession_id=loaded_service.profession_id) |
            Q(tags__in=loaded_service.tags.all())
        ).exclude(id=loaded_service.id).distinct()
        context['related_services'] = related_services

        return context