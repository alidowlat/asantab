from django import forms
from core.clean import OTPCleanMixin, PhoneNumberCleanMixin


class PhoneForm(PhoneNumberCleanMixin, forms.Form):
    phone_number = forms.CharField(
        max_length=11,
    )


class OTPForm(OTPCleanMixin, forms.Form):
    otp = forms.CharField(
        error_messages={
            'required': 'وارد کردن کد الزامی است.',
        },
    )


class PasswordVerifyForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
