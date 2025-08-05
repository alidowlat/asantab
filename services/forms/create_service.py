from django import forms
from django.forms import inlineformset_factory
from locations.models import Province
from services.models import (
    Service, Schedule, Option
)


class ServiceForm(forms.ModelForm):
    province = forms.ModelChoiceField(queryset=Province.objects.all(), required=True)

    class Meta:
        model = Service
        fields = [
            'title', 'slug', 'description', 'image',
            'platform', 'platform_link',
            'category', 'profession', 'tags',
            'is_active'
        ]


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['date', 'capacity', 'is_active']
        widgets = {
            'date': forms.TextInput(attrs={
                'id': 'jalali-input',
                'class': 'w-full sm:max-w-[180px] rounded-lg border bg-background text-center px-3 py-2',
                'placeholder': 'تاریخ را انتخاب کنید'
            })
        }


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['title', 'unit_price', 'is_active']


ScheduleFormSet = inlineformset_factory(Service, Schedule, form=ScheduleForm, extra=1, can_delete=True)
OptionFormSet = inlineformset_factory(Service, Option, form=OptionForm, extra=1, can_delete=True)
