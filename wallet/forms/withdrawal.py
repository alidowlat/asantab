from django import forms
from accounts.models import BankAccount
from wallet.models import WithdrawalRequest


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ["amount", "bank_account"]

    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        label="انتخاب حساب بانکی"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["bank_account"].queryset = BankAccount.objects.filter(user=user)
