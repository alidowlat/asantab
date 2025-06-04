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