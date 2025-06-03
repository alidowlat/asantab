from django import forms

from core.clean import OTPCleanMixin
from core.convertors import fa_to_en_digits


class PhoneForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11,
    )

    def clean_phone_number(self):
        phone = fa_to_en_digits(self.cleaned_data['phone_number'].strip())
        errors = []

        if not phone.isdigit():
            errors.append("شماره موبایل نامعتبر است.")

        if not phone.startswith("09"):
            errors.append("شماره موبایل میبایست با ۰۹ شروع شود.")

        if len(phone) != 11:
            errors.append("شماره موبایل میبایست دقیقا ۱۱ رقمی باشد.")

        if errors:
            raise forms.ValidationError(errors)

        return phone


class OTPForm(OTPCleanMixin, forms.Form):
    otp = forms.CharField(
        error_messages={
            'required': 'وارد کردن کد الزامی است.',
        },
    )
