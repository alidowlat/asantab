import os
from django import forms
from accounts.models import Provider
from core.clean import UsernameCleanMixin, IbanNumberCleanMixin, CardNumberCleanMixin
from django.conf import settings


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