from django import forms
from django.forms import inlineformset_factory

from locations.models import City
from services.models import (
    Service, Schedule, Option
)


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'title', 'slug', 'description', 'image',
            'platform', 'platform_link',
            'category', 'profession', 'locations', 'tags',
            'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['locations'].queryset = City.objects.select_related('province').all()


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['date', 'is_active', 'capacity']


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['title', 'unit_price', 'is_active']


ScheduleFormSet = inlineformset_factory(Service, Schedule, form=ScheduleForm, extra=1, can_delete=True)
OptionFormSet = inlineformset_factory(Service, Option, form=OptionForm, extra=1, can_delete=True)
