from django import forms
from django.forms import inlineformset_factory
from locations.models import Province
from services.models import (
    Service, Schedule, Option
)


class ServiceForm(forms.ModelForm):
    province = forms.ModelChoiceField(queryset=Province.objects.all(), required=True)
    platform_username = forms.CharField(required=True)

    class Meta:
        model = Service
        fields = [
            'title', 'slug', 'description', 'image',
            'platform', 'platform_link',
            'category', 'profession', 'tags',
            'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance and instance.platform and instance.platform_link:
            prefix_map = {
                'instagram': 'https://instagram.com/',
                'telegram': 'https://t.me/',
                'youtube': 'https://youtube.com/',
            }

            prefix = prefix_map.get(instance.platform.slug.lower())
            if prefix and instance.platform_link.startswith(prefix):
                self.fields['platform_username'].initial = instance.platform_link[len(prefix):]
            else:
                self.fields['platform_username'].initial = instance.platform_link

    def clean(self):
        cleaned = super().clean()
        platform = cleaned.get('platform')
        username = cleaned.get('platform_username', '').strip()

        if not platform or not username:
            return cleaned

        prefix_map = {
            'instagram': 'https://instagram.com/',
            'telegram': 'https://t.me/',
            'youtube': 'https://youtube.com/',
        }
        prefix = prefix_map.get(platform.slug.lower(), '')
        cleaned['platform_link'] = prefix + username.lstrip('@/')

        return cleaned


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
