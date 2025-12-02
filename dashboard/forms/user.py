from django import forms
from django.core.exceptions import ValidationError
from khayyam import JalaliDate
from accounts.models import User
from core.convertors import fa_to_en_digits
from orders.models import OrderContent


class OrderContentForm(forms.ModelForm):
    # files = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = OrderContent
        fields = ['description']

        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 5,
                "id": "description-section",
                "class": "block w-full rounded-lg bg-background border border-border p-2.5 text-sm text-text shadow-sm focus:border-emerald-500 focus:ring-emerald-500 dark:focus:border-emerald-500 dark:focus:ring-emerald-500 dark:placeholder-text/50 sm:text-base",
                "placeholder": "لطفا جزئیات محتوای مد نظر خود را با دقت شرح دهید...",
            }),
        }

        error_messages = {
            'description': {
                'required': 'وارد کردن این فیلد الزامی است.',
            },
        }


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
                'invalid': 'شماره موبایل وارد شده معتبر نیست.',
            },
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_number = fa_to_en_digits(phone_number or '')

        if not phone_number:
            if self.instance.phone_number:
                raise ValidationError("نمی‌توانید شماره موبایل را خالی بگذارید.")
            raise ValidationError("وارد کردن شماره موبایل الزامی است.")

        if not phone_number.isdigit() or len(phone_number) != 11:
            raise ValidationError("شماره موبایل باید دقیقاً ۱۱ رقم عددی باشد.")

        if not phone_number.startswith("09"):
            raise ValidationError("شماره موبایل باید با 09 شروع شود.")

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
                'invalid': 'شماره موبایل وارد شده معتبر نیست.',
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

        qs = User.objects.filter(national_id=national_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("این کد ملی قبلاً در وبسایت ثبت شده است.")

        return national_id


class UpdateGenderForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['gender']

        widgets = {
            'gender': forms.Select(attrs={'class': 'modal-input'}),
        }

        error_messages = {
            'gender': {
                'required': 'لطفا گزینه مورد نظر را انتخاب کنید.',
            },
        }


class UpdateBirthdateForm(forms.ModelForm):
    birth_day = forms.ChoiceField(choices=[(i, i) for i in range(1, 32)], label='روز')
    birth_month = forms.ChoiceField(choices=[
        (1, 'فروردین'), (2, 'اردیبهشت'), (3, 'خرداد'), (4, 'تیر'),
        (5, 'مرداد'), (6, 'شهریور'), (7, 'مهر'), (8, 'آبان'),
        (9, 'آذر'), (10, 'دی'), (11, 'بهمن'), (12, 'اسفند')
    ], label='ماه')
    birth_year = forms.ChoiceField(choices=[(y, y) for y in range(1300, 1405)], label='سال')

    class Meta:
        model = User
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        try:
            year = int(cleaned_data.get('birth_year'))
            month = int(cleaned_data.get('birth_month'))
            day = int(cleaned_data.get('birth_day'))
            jalali_date = JalaliDate(year, month, day)
            miladi = jalali_date.todate()
        except Exception:
            raise forms.ValidationError("تاریخ وارد شده معتبر نیست.")

        cleaned_data['birth_date'] = miladi
        return cleaned_data

    def save(self, commit=True):
        self.instance.birth_date = self.cleaned_data['birth_date']
        return super().save(commit=commit)
