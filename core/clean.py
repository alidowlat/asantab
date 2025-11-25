from django.core.exceptions import ValidationError
from core.convertors import fa_to_en_digits
from accounts.models import Provider
from django import forms
import re


class PlatformLinkCleanMixin(forms.Form):
    def clean_url(self):
        url = self.cleaned_data.get('url', '').strip()

        if url.startswith('https://'):
            url = url[len('https://'):]

        url = fa_to_en_digits(url)

        if not re.match(r'^[\w\-\./?=&]+$', url):
            raise ValidationError('آدرس وارد شده معتبر نیست.')

        if len(url) < 5:
            raise ValidationError('آدرس باید حداقل ۵ کاراکتر داشته باشد.')

        return url

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url', '')
        cleaned_data['url'] = 'https://' + url
        return cleaned_data


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


class IbanNumberCleanMixin(forms.Form):
    def clean_iban_number(self):
        if self.cleaned_data.get('iban_number'):
            iban = self.cleaned_data.get('iban_number', '').replace(' ', '')
            iban = fa_to_en_digits(iban)
            if not iban.isdigit() or len(iban) != 24:
                raise ValidationError('شماره شبا باید شامل ۲۴ رقم عددی باشد.')
            return iban
        return ''


class CardNumberCleanMixin(forms.Form):
    def clean_card_number(self):
        if self.cleaned_data.get('card_number'):
            card = self.cleaned_data.get('card_number', '').replace(' ', '')
            card = fa_to_en_digits(card)
            if not card.isdigit() or len(card) != 16:
                raise ValidationError('شماره کارت باید ۱۶ رقم عددی باشد.')
            return card
        return ''


class PhoneNumberCleanMixin(forms.Form):
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


class PasswordCleanMixin(forms.Form):
    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get('new_password')
        confirm_password = cleaned.get('confirm_password')

        if not new_password:
            self.add_error('new_password', 'کلمه عبور جدید وارد نشده است.')
        else:
            if len(new_password) < 8 or len(new_password) > 24:
                self.add_error('new_password', 'طول کلمه عبور باید بین ۸ تا ۲۴ کاراکتر باشد.')
            if not re.search(r'[a-z]', new_password):
                self.add_error('new_password', 'کلمه عبور باید حداقل یک حرف کوچک داشته باشد.')
            if not re.search(r'[A-Z]', new_password):
                self.add_error('new_password', 'کلمه عبور باید حداقل یک حرف بزرگ داشته باشد.')
            if not re.search(r'\d', new_password):
                self.add_error('new_password', 'کلمه عبور باید حداقل یک عدد داشته باشد.')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'تکرار کلمه عبور با کلمه عبور جدید مطابقت ندارد.')

        return cleaned


def create_visit_clean(
        user,
        model,
        request,
        fk_name: str,
        http_service,
        loaded_obj
):
    ip, user_agent, referer = http_service(request)

    filter_kwargs = {
        'ip': ip,
        fk_name: loaded_obj,
    }

    if not model.objects.filter(**filter_kwargs).exists():
        model.objects.create(
            **filter_kwargs,
            user=user if user.is_authenticated else None,
            user_agent=user_agent,
            referer=referer,
        )
