from django import forms
from django.core.exceptions import ValidationError

from core.clean import OTPCleanMixin
from core.convertors import fa_to_en_digits


class PhoneNumberChangeForm(forms.Form):
    phone_number = forms.CharField(max_length=11)

    def clean_phone_number(self):
        phone_number = fa_to_en_digits(self.cleaned_data['phone_number'])
        errors = []

        if not phone_number:
            errors.append("وارد کردن شماره موبایل الزامی است.")

        if not phone_number.startswith("09"):
            errors.append("شماره موبایل باید با 09 شروع شود.")

        if not phone_number.isdigit() or len(phone_number) != 11:
            errors.append("شماره موبایل باید دقیقاً ۱۱ رقم عددی باشد.")

        if errors:
            raise ValidationError(errors)

        return phone_number


class PhoneNumberVerifyForm(OTPCleanMixin, forms.Form):
    otp = forms.CharField(
        error_messages={
            'required': 'وارد کردن کد الزامی است.',
        },
    )
