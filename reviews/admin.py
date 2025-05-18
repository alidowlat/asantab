from django.contrib import admin

from reviews.models.service_review import ServiceReview, ServiceReviewReaction

admin.site.register(ServiceReview)
admin.site.register(ServiceReviewReaction)