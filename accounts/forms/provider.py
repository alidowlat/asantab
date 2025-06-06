from accounts.models import Provider
from django import forms
from core.clean import UsernameCleanMixin, IbanNumberCleanMixin, CardNumberCleanMixin, PhoneNumberCleanMixin


class ProviderLoginForm(PhoneNumberCleanMixin, forms.Form):
    phone_number = forms.CharField(max_length=11)
    password = forms.CharField(widget=forms.PasswordInput)


class ProviderCompleteInfoForm(UsernameCleanMixin, IbanNumberCleanMixin, CardNumberCleanMixin, forms.ModelForm):
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

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('province'):
            self.add_error('province', 'انتخاب استان الزامی است.')

        if not cleaned_data.get('city'):
            self.add_error('city', 'انتخاب شهر الزامی است.')

        if not cleaned_data.get('username'):
            self.add_error('username', 'وارد کردن نام کاربری الزامی است.')
