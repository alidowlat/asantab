from django import forms
from django.core import validators


class DiscountForm(forms.Form):
    discount_code = forms.CharField(
        validators=[
            validators.MaxLengthValidator(50)
        ]
    )
