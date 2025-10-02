from django import forms
from tickets.models import TicketMessage, Ticket, TicketDepartment


class TicketForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=TicketDepartment.objects.all(),
        empty_label="انتخاب کنید",
    )

    class Meta:
        model = Ticket
        fields = ["department", "subject"]


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ["message", "attachment"]
        widgets = {
            "message": forms.Textarea(attrs={
                "rows": 5,
                "id": "reply-message",
                "class": "block w-full rounded-lg bg-background border border-border p-2.5 text-sm text-text shadow-sm focus:border-emerald-500 focus:ring-emerald-500 dark:focus:border-emerald-500 dark:focus:ring-emerald-500 dark:placeholder-text/50 sm:text-base",
                "placeholder": "لطفا جزئیات درخواست خود را با دقت شرح دهید...",
            }),
            "attachment": forms.ClearableFileInput(attrs={
                "class": "hidden",
                "id": "attachment-input",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        message = cleaned_data.get("message")
        attachment = cleaned_data.get("attachment")
        if not message and not attachment:
            raise forms.ValidationError("لطفا پیام یا فایل ضمیمه را وارد کنید.")
        return cleaned_data
