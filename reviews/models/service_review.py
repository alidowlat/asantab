from django.db import models

from config.models import BaseReview, BaseReviewReaction


class ServiceReview(BaseReview):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='reviews', verbose_name='خدمت')

    class Meta:
        verbose_name = 'Service Review'
        verbose_name_plural = 'Service Reviews'
        db_table = 'services_reviews'


class ServiceReviewReaction(BaseReviewReaction):
    review = models.ForeignKey(ServiceReview, on_delete=models.CASCADE, related_name='reactions', verbose_name='نظر')

    class Meta:
        unique_together = ('user', 'review')
        verbose_name = 'Service Review Reaction'
        verbose_name_plural = 'Service Review Reactions'
        db_table = 'services_review_reactions'

    def __str__(self):
        return f"{self.reaction} - {self.review}"