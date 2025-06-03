from django.core.exceptions import ValidationError
from core.convertors import fa_to_en_digits
from accounts.models import Provider
from django import forms
import re


class UsernameCleanMixin(forms.Form):
    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        username = fa_to_en_digits(username).replace(' ', '')

        instance = getattr(self, 'instance', None)
        if Provider.objects.exclude(pk=instance.pk).filter(username=username).exists():
            raise ValidationError('این نام کاربری قبلا در وب سایت ثبت شده.', code='duplicate_username')

        if len(username) < 5:
            raise ValidationError('نام کاربری باید حداقل ۵ حرف باشد.')

        if not re.fullmatch(r'[a-zA-Z0-9_]+', username):
            raise ValidationError('در وارد کردن نام کاربری فقط حروف انگلیسی، اعداد و "_" مجاز است.')

        if username[0].isdigit():
            raise ValidationError('نام کاربری نمی‌تواند با عدد شروع شود.')

        return username


class BankCleanMixin(forms.Form):
    def clean_iban_number(self):
        if self.cleaned_data.get('iban_number'):
            iban = self.cleaned_data.get('iban_number', '').replace(' ', '')
            iban = fa_to_en_digits(iban)
            if not iban.isdigit() or len(iban) != 24:
                raise ValidationError('شماره شبا باید شامل ۲۴ رقم عددی باشد.')
            return iban
        return ''

    def clean_card_number(self):
        if self.cleaned_data.get('card_number'):
            card = self.cleaned_data.get('card_number', '').replace(' ', '')
            card = fa_to_en_digits(card)
            if not card.isdigit() or len(card) != 16:
                raise ValidationError('شماره کارت باید ۱۶ رقم عددی باشد.')
            return card
        return ''


class OTPCleanMixin(forms.Form):
    def clean_otp(self):
        otp = fa_to_en_digits(self.cleaned_data['otp'].strip())
        errors = []

        if not otp.isdigit():
            errors.append("کد تایید میبایست فقط عدد باشد.")

        if len(otp) != 5:
            errors.append("کد تایید میبایست دقیقا ۵ رقمی باشد.")

        if errors:
            raise forms.ValidationError(errors)

        return otp