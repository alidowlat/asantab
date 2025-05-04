from django.views.generic import ListView
from services.models import Service


class ServiceListView(ListView):
    template_name = 'services/list.html'
    model = Service
    context_object_name = 'services'
    ordering = ['-id']
    paginate_by = 8

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        latest_service = self.object_list.first()
        context['latest_service'] = latest_service

        if latest_service:
            prices = [opt.unit_price for opt in latest_service.options.all() if opt.unit_price is not None]
            context['min_price'] = min(prices) if prices else None
            context['max_price'] = max(prices) if prices else None

        return context

        # db_max_price = Service.new_price if Service is not None else 0
        # context['start_price'] = self.request.GET.get('start_price') or 0
        # context['end_price'] = self.request.GET.get('end_price') or db_max_price
        #
        # most_bought_Services = Service.objects.filter(orderdetails__order__is_paid=True).annotate(
        #     order_count=Sum('orderdetails__count')
        # ).order_by('-order_count')[:12]
        # context['most_bought_Services'] = group_list(most_bought_Services)
        #
        # most_visit_Services = Service.objects.filter(is_active=True).annotate(
        #     visit_count=Count('Servicevisit')).order_by('-visit_count')[:13]
        # context['most_visit_Services'] = most_visit_Services
        #
        # high_price_Services = Service.objects.filter(is_active=True, is_stock=True).order_by('-new_price')[:13]
        # context['high_price_Services'] = high_price_Services
        #
        # low_price_Services = Service.objects.filter(is_active=True, is_stock=True).order_by('new_price')[:13]
        # context['low_price_Services'] = low_price_Services
