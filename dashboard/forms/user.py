from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User
from core.convertors import fa_to_en_digits


class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'email': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'ایمیل وارد شده معتبر نیست.',
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email and self.instance.email:
            raise ValidationError("نمی‌توانید ایمیل را خالی بگذارید.")

        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('این ایمیل قبلا در وب سایت ثبت شده.', code='duplicate_email')

        return email


class UpdateNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'modal-input'}),
            'last_name': forms.TextInput(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'first_name': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'نام وارد شده معتبر نیست.',
            },
            'last_name': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'نام حانوادگی وارد شده معتبر نیست.',
            },
        }

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name') or ''
        if not last_name.strip() and self.instance.last_name:
            raise ValidationError("نمی‌توانید نام خانوادگی را خالی بگذارید.")

        return last_name


class UpdatePhoneForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number']

        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'phone_number': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'شماره تماس وارد شده معتبر نیست.',
            },
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_number = fa_to_en_digits(phone_number or '')

        if not phone_number:
            if self.instance.phone_number:
                raise ValidationError("نمی‌توانید شماره تماس را خالی بگذارید.")
            raise ValidationError("وارد کردن شماره تماس الزامی است.")

        if not phone_number.isdigit() or len(phone_number) != 11:
            raise ValidationError("شماره تماس باید دقیقاً ۱۱ رقم عددی باشد.")

        if not phone_number.startswith("09"):
            raise ValidationError("شماره تماس باید با 09 شروع شود.")

        return phone_number


class UpdateNationalIDForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['national_id']

        widgets = {
            'national_id': forms.TextInput(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'national_id': {
                'required': 'وارد کردن این فیلد الزامی است.',
                'invalid': 'شماره تماس وارد شده معتبر نیست.',
            },
        }

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        national_id = fa_to_en_digits(national_id or '')

        if not national_id:
            if self.instance.national_id:
                raise ValidationError("نمی‌توانید کد ملی را خالی بگذارید.")
            raise ValidationError("وارد کردن کد ملی الزامی است.")

        if not national_id.isdigit() or len(national_id) != 10:
            raise ValidationError("کد ملی باید دقیقاً 10 رقم عددی باشد.")

        return national_id
