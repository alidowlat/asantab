from django.db.models import Q, Min, Max, Count
from reviews.models import ServiceReview
from services.models import Schedule, Service


class ServiceDataFetcher:
    def __init__(self, service):
        self.service = service

    def get_price_range(self):
        return self.service.options.aggregate(
            min_price=Min('unit_price'), max_price=Max('unit_price')
        )

    def get_related_services(self):
        return Service.objects.filter(
            Q(profession__in=self.service.profession.all()) |
            Q(tags__in=self.service.tags.all())
        ).exclude(id=self.service.id).distinct()

    def get_schedules(self):
        return Schedule.objects.filter(
            is_active=True, service=self.service, capacity__gte=1
        ).distinct()

    def get_annotated_reviews(self):
        base_qs = ServiceReview.objects.filter(
            service=self.service,
            status='approved'
        ).select_related('user')

        annotated = base_qs.annotate(
            like_count=Count('reactions', filter=Q(reactions__reaction='like')),
            dislike_count=Count('reactions', filter=Q(reactions__reaction='dislike')),
        ).order_by('-created_at')

        return annotated, base_qs.count()