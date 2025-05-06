from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max, Min
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from services.models import Service


class ServiceListView(ListView):
    template_name = 'services/list.html'
    model = Service
    context_object_name = 'services'
    ordering = ['-id']
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        latest_service = self.object_list.first()
        context['latest_service'] = latest_service

        for service in context['services']:
            prices = list(service.options.filter(unit_price__isnull=False).values_list('unit_price', flat=True))
            service.min_price = min(prices) if prices else None
            service.max_price = max(prices) if prices else None

        return context

    def get_queryset(self):
        request = self.request
        sort_by = request.GET.get('sort_by')
        category = request.GET.get('category')
        profession = request.GET.get('profession')
        is_active = request.GET.get('is_active')
        is_unique = request.GET.get('is_unique')

        query = Service.objects.filter(options__is_active=True).annotate(
            min_price=Min('options__unit_price'),
            max_price=Max('options__unit_price')
        ).distinct()

        if category:
            query = query.filter(category__url_title__in=category.split(','))

        if profession:
            query = query.filter(profession__url_title__in=profession.split(','))

        if is_active == 'True':
            query = query.filter(is_active=True)
        elif is_active == 'False':
            query = query.filter(is_active=False)

        if is_unique == 'True':
            query = query.filter(is_unique=True)

        match sort_by:
            case 'expensive':
                query = query.order_by('-max_price', '-id')
            case 'cheap':
                query = query.order_by('min_price', '-id')
            case 'newest':
                query = query.order_by('-id')
            case 'oldest':
                query = query.order_by('id')

        return query

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


@staff_member_required
@require_POST
def toggle_unique_status(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_unique = not service.is_unique
    service.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
