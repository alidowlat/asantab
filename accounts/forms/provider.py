import re
from django.core.exceptions import ValidationError
from accounts.models import Provider
from django import forms
from core.convertors import fa_to_en_digits


class ProviderCompleteInfoForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = [
            'username',
            'bio',
            'province',
            'city',
            'profile_image',
            'iban_number',
            'card_number',
            'national_card_image',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'درباره خودت بنویس...'}),
            'username': forms.TextInput(attrs={'placeholder': 'مثلاً alikarimi'}),
            'province': forms.Select(),
            'city': forms.Select(),
            'iban_number': forms.TextInput(attrs={'placeholder': 'مثلاً IR220170000000000000123456'}),
            'card_number': forms.TextInput(attrs={'placeholder': 'مثلاً 6037991234567890'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        username = fa_to_en_digits(username).replace(' ', '')

        if len(username) < 5:
            raise ValidationError('نام کاربری باید حداقل ۵ حرف باشد.')

        if not re.fullmatch(r'[a-zA-Z0-9_]+', username):
            raise ValidationError('در وارد کردن نام کاربری فقط حروف انگلیسی، اعداد و "_" مجاز است.')

        if username[0].isdigit():
            raise ValidationError('نام کاربری نمی‌تواند با عدد شروع شود.')

        return username

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

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('province'):
            self.add_error('province', 'انتخاب استان الزامی است.')

        if not cleaned_data.get('city'):
            self.add_error('city', 'انتخاب شهر الزامی است.')

        if not cleaned_data.get('username'):
            self.add_error('username', 'وارد کردن نام کاربری الزامی است.')
