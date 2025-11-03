from accounts.models import Provider
from django import forms
from core.clean import UsernameCleanMixin, PhoneNumberCleanMixin, PasswordCleanMixin


class ProviderLoginForm(PhoneNumberCleanMixin, forms.Form):
    phone_number = forms.CharField(max_length=11)
    password = forms.CharField(widget=forms.PasswordInput)


class ProviderCompleteInfoForm(UsernameCleanMixin, forms.ModelForm):
    first_name = forms.CharField(
        max_length=40,
        required=True,
        label="نام",
        widget=forms.TextInput(attrs={'placeholder': 'مثلاً علی'})
    )
    last_name = forms.CharField(
        max_length=40,
        required=True,
        label="نام خانوادگی",
        widget=forms.TextInput(attrs={'placeholder': 'مثلاً دولت'})
    )

    class Meta:
        model = Provider
        fields = [
            'username',
            'bio',
            'province',
            'city',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'درباره خودت بنویس...'}),
            'username': forms.TextInput(attrs={'placeholder': 'مثلاً alikarimi'}),
            'province': forms.Select(),
            'city': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name

    def save(self, commit=True):
        provider = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            if commit:
                self.user.save(update_fields=["first_name", "last_name"])
        if commit:
            provider.save()
        return provider


class ProviderForgotPhoneForm(forms.Form):
    phone_number = forms.CharField(max_length=20)


class ProviderResetWithOTPForm(PasswordCleanMixin, forms.Form):
    otp = forms.CharField(
        required=True,
        error_messages={'required': 'کد تأیید الزامی است.'},
        max_length=5
    )
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp:
            raise forms.ValidationError("فیلد کد تأیید نمی‌تواند خالی باشد.")
        return otp