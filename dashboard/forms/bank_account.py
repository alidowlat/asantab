from django import forms
from accounts.models import BankAccount


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["sheba_number", "card_number"]
        exclude = ["bank"]
        widgets = {
            "sheba_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "مثلاً: 650180000000000216XXXXXX"}),
            "card_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "مثلاً: 6037XXXX2565XXXX"}),
        }
        error_messages = {
            "sheba_number": {
                "required": "وارد کردن شماره شبا الزامی است.",
                "invalid": "شماره شبا باید ۲۴ رقم عددی باشد.",
                "unique": "این شماره شبا قبلاً در وب سایت ثبت شده است.",
            },
            "card_number": {
                "required": "وارد کردن شماره کارت الزامی است.",
                "invalid": "شماره کارت باید ۱۶ رقم عددی باشد.",
                "unique": "این شماره کارت قبلاً در وب سایت ثبت شده است.",
            },
        }
