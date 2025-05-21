from django.db import models

from config.models import BaseFavorite


class Favorite(BaseFavorite):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='favorites', verbose_name='خدمت')

    class Meta:
        unique_together = ('user', 'service')
        db_table = 'favorite_services'
