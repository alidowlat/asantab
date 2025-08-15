import os
from django import forms
from accounts.models import Provider
from core.clean import UsernameCleanMixin, IbanNumberCleanMixin, CardNumberCleanMixin, PasswordCleanMixin, PlatformLinkCleanMixin
from django.conf import settings
from locations.models import City


class UpdatePlatformUrlsForm(PlatformLinkCleanMixin, forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['instagram_url', 'telegram_url']
        widgets = {
            'instagram_url': forms.URLInput(attrs={
                'class': 'modal-input peer w-full rounded-lg bg-transparent p-2 placeholder-transparent outline-none focus:ring-0 xs:px-4 xs:py-3',
                'dir': 'ltr',
                'value': 'https://',
                'readonly': False
            }),
            'telegram_url': forms.URLInput(attrs={
                'class': 'modal-input peer w-full rounded-lg bg-transparent p-2 placeholder-transparent outline-none focus:ring-0 xs:px-4 xs:py-3',
                'dir': 'ltr',
                'value': 'https://',
                'readonly': False
            }),
        }
        error_messages = {
            'instagram_url': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'آدرس وارد شده معتبر نیست.',
            },
            'telegram_url': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'آدرس وارد شده معتبر نیست.',
            }
        }


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


class UpdateIbanForm(IbanNumberCleanMixin, forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['iban_number']

        widgets = {
            'iban_number': forms.TextInput(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'iban_number': {
                'required': 'وارد کردن این فیلد الزامی است.',
            },
        }


class UpdateCardNumberForm(CardNumberCleanMixin, forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['card_number']

        widgets = {
            'card_number': forms.TextInput(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'card_number': {
                'required': 'وارد کردن این فیلد الزامی است.',
            },
        }


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
