import os
from django import forms
from accounts.models import Provider
from core.clean import UsernameCleanMixin, IbanNumberCleanMixin, CardNumberCleanMixin, PasswordCleanMixin, PlatformLinkCleanMixin
from django.conf import settings
from locations.models import City
from django.core.exceptions import ValidationError


class FixedPrefixURLInput(forms.TextInput):
    def __init__(self, prefix, *args, **kwargs):
        self.prefix = prefix
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        if value is None:
            value = ''
        if not value.startswith(self.prefix):
            value = self.prefix
        return value


class UpdatePlatformUrlsForm(forms.ModelForm):
    instagram_url = forms.CharField(
        required=False,
        widget=FixedPrefixURLInput(prefix='https://instagram.com/', attrs={
            'class': 'modal-input peer w-full rounded-lg bg-transparent p-2 placeholder-transparent outline-none focus:ring-0 xs:px-4 xs:py-3',
            'dir': 'ltr',
            'readonly': False
        })
    )
    telegram_url = forms.CharField(
        required=False,
        widget=FixedPrefixURLInput(prefix='https://t.me/', attrs={
            'class': 'modal-input peer w-full rounded-lg bg-transparent p-2 placeholder-transparent outline-none focus:ring-0 xs:px-4 xs:py-3',
            'dir': 'ltr',
            'readonly': False
        })
    )

    class Meta:
        model = Provider
        fields = ['instagram_url', 'telegram_url']

    def clean_instagram_url(self):
        url = self.cleaned_data.get('instagram_url', '')
        prefix = 'https://instagram.com/'
        if url and not url.startswith(prefix):
            raise ValidationError(f'آدرس باید با {prefix} شروع شود.')
        return url

    def clean_telegram_url(self):
        url = self.cleaned_data.get('telegram_url', '')
        prefix = 'https://t.me/'
        if url and not url.startswith(prefix):
            raise ValidationError(f'آدرس باید با {prefix} شروع شود.')
        return url


class UpdateUsernameForm(UsernameCleanMixin, forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['username']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'username': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'ایمیل وارد شده معتبر نیست.',
            },
        }


class UpdateBioForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['bio']

        widgets = {
            'bio': forms.Textarea(attrs={'class': 'modal-input', 'rows': 6}),
        }

        error_messages = {
            'bio': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'ایمیل وارد شده معتبر نیست.',
            },
        }

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if len(bio) > 500:
            raise forms.ValidationError('حداکثر ۵۰۰ کاراکتر برای درباره من مجاز است.')
        return bio


class UpdateLocationForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['province', 'city']

        widgets = {
            'province': forms.Select(attrs={'class': 'modal-input'}),
            'city': forms.Select(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'province': {
                'required': 'وارد کردن این فیلد الزامی است.',
            },
            'city': {
                'required': 'وارد کردن این فیلد الزامی است.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['city'].queryset = City.objects.select_related('province').all()


class UpdateNationalCardImageForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['national_card_image']

        error_messages = {
            'national_card_image': {
                'required': 'وارد کردن این فیلد الزامی است.',
            },
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        new_image = self.cleaned_data.get('national_card_image')
        if new_image:
            old_image = Provider.objects.filter(pk=instance.pk).values_list('national_card_image', flat=True).first()
            if old_image:
                old_path = os.path.join(settings.MEDIA_ROOT, old_image)
                if os.path.isfile(old_path):
                    os.remove(old_path)

        if commit:
            instance.save()
        return instance


class UpdateProfileImageForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['profile_image']

        error_messages = {
            'profile_image': {
                'required': 'وارد کردن این فیلد الزامی است.',
            },
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        new_image = self.cleaned_data.get('profile_image')
        if new_image:
            old_image = Provider.objects.filter(pk=instance.pk).values_list('profile_image', flat=True).first()
            if old_image:
                old_path = os.path.join(settings.MEDIA_ROOT, old_image)
                if os.path.isfile(old_path):
                    os.remove(old_path)

        if commit:
            instance.save()
        return instance


class UpdatePasswordForm(PasswordCleanMixin, forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'modal-input'}),
        error_messages={'required': 'وارد کردن کلمه عبور قبلی الزامی است.'}
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'modal-input'}),
        error_messages={'required': 'وارد کردن کلمه عبور جدید الزامی است.'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'modal-input'}),
        error_messages={'required': 'تکرار کلمه عبور جدید الزامی است.'}
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if not self.user.has_usable_password():
            self.fields.pop('old_password')
