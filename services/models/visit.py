from django.db import models
from config.models import BaseVisit


class ServiceVisit(BaseVisit):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='visits', verbose_name='خدمت')

    def __str__(self):
        return f'{self.service.title} / {self.ip}'

    class Meta:
        db_table = 'services_visits'
