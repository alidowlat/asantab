from accounts.models import Provider
from django import forms


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
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری'}),
            'province': forms.Select(),
            'city': forms.Select(),
            'iban_number': forms.TextInput(attrs={'placeholder': 'مثلاً IRxxxxxxxxxxxxxxxxxxxxxx'}),
            'card_number': forms.TextInput(attrs={'placeholder': 'مثلاً 603729xxxxxxxxxx'}),
        }
