from django import forms
from accounts.models import Provider
from core.clean import UsernameCleanMixin


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
