from django import forms
from tickets.models import ContactUs
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'نام'}),
            'email': forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'ایمیل'}),
            'subject': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'موضوع'}),
            'message': forms.Textarea(attrs={'class': 'input-field', 'placeholder': 'پیام شما'}),
        }
        error_messages = {
            'name': {'required': 'وارد کردن نام الزامی است.'},
            'email': {'required': 'وارد کردن ایمیل الزامی است.', 'invalid': 'ایمیل معتبر نیست.'},
            'subject': {'required': 'وارد کردن موضوع الزامی است.'},
            'message': {'required': 'وارد کردن پیام الزامی است.'},
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('ایمیل معتبر نیست.')
        return email
