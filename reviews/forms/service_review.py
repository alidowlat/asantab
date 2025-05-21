from django import forms

from reviews.models import ServiceReview


class ServiceReviewForm(forms.ModelForm):
    class Meta:
        model = ServiceReview
        fields = ['service', 'title', 'text', 'recommendation']
