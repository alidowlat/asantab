from django import forms
from django.core import validators


class PhoneForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11,
        validators=[
            validators.RegexValidator(
                regex=r'^09\d{9}$',
                message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد.'
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'مثلاً 09123456789'})
    )


class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=5,
        min_length=5,
        error_messages={
            'required': 'وارد کردن کد الزامی است.',
            'min_length': 'کد باید دقیقاً ۵ رقم باشد.',
            'max_length': 'کد باید دقیقاً ۵ رقم باشد.',
        },
        validators=[validators.RegexValidator(r'^\d{5}$', 'کد باید ۵ رقمی و عددی باشد.')],
        widget=forms.TextInput(attrs={'placeholder': 'کد ۵ رقمی'})
    )
