from django import forms
from accounts.models import BankAccount
from wallet.models import WithdrawalRequest


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ["amount", "bank_account"]

    amount = forms.DecimalField(
        label="مبلغ برداشت",
        error_messages={
            'required': 'وارد کردن مبلغ الزامی است.',
            'invalid': 'لطفاً یک عدد معتبر وارد کنید.'
        }
    )

    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        label="انتخاب حساب بانکی",
        error_messages={
            "required": "لطفاً یک حساب بانکی انتخاب کنید."
        }
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["bank_account"].queryset = BankAccount.objects.filter(user=user)
