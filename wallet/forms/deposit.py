from django import forms

class DepositForm(forms.Form):
    amount = forms.IntegerField(
        min_value=10000,
        label="مبلغ واریز (تومان)",
        error_messages={
            "min_value": "مبلغ وارد شده کمتر از حداقل مجاز است. حداقل مبلغ واریز ۱۰,۰۰۰ تومان می‌باشد.",
            "required": "لطفاً مبلغ را وارد کنید.",
            "invalid": "لطفاً فقط عدد وارد کنید."
        },
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "مثلاً: ۵۰،۰۰۰",
        })
    )
