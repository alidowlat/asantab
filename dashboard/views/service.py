from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_POST
from accounts.models import Provider
from locations.models import City, Province
from services.forms import ServiceForm, ScheduleFormSet, OptionFormSet, OptionForm, ScheduleForm
from django.views.generic import ListView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from services.models import Service, Option, Schedule


class ProviderServiceList(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'dashboard/services/main.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(provider__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = get_object_or_404(Provider, user=self.request.user)
        context['provider'] = provider
        return context


class ProviderServiceCreate(LoginRequiredMixin, View):
    template_name = 'dashboard/services/create.html'

    def get_context_data(self):
        provinces = Province.objects.all()
        return {
            'service_form': ServiceForm(),
            'option_formset': OptionFormSet(prefix='option'),
            'schedule_formset': ScheduleFormSet(prefix='schedule'),
            'provinces': provinces,
            'selected_cities': [],
            'selected_city_ids': [],
            'selected_province_id': None,
            'is_edit': False
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': True, 'html': html})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        service_form = ServiceForm(request.POST, request.FILES)
        option_formset = OptionFormSet(request.POST, request.FILES, prefix='option')
        schedule_formset = ScheduleFormSet(request.POST, request.FILES, prefix='schedule')

        global_error = None

        if service_form.is_valid() and option_formset.is_valid() and schedule_formset.is_valid():
            service = service_form.save(commit=False)
            provider = get_object_or_404(Provider, user=self.request.user)
            service.provider = provider
            service.save()

            city_ids = [int(cid) for cid in request.POST.get("cities", "").split(",") if cid]
            service.locations.set(city_ids)

            profession_ids = [int(pid) for pid in request.POST.get("profession", "").split(",") if pid]
            service.profession.set(profession_ids)

            tag_ids = [int(tid) for tid in request.POST.get("tags", "").split(",") if tid]
            service.tags.set(tag_ids)

            for opt in option_formset.save(commit=False):
                if not getattr(opt, 'title', '').strip():
                    continue
                opt.service = service
                opt.save()

            for schedule in schedule_formset.save(commit=False):
                if not getattr(schedule, 'date', None):
                    continue
                schedule.service = service
                schedule.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse("provider_service_list")})
            return redirect("provider_service_list")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors_html = render_to_string(
                'dashboard/services/errors.html',
                {
                    'service_form': service_form,
                    'option_formset': option_formset,
                    'schedule_formset': schedule_formset,
                    'global_error': global_error
                },
                request=request
            )
            return JsonResponse({'success': False, 'errors_html': errors_html})

        return render(request, self.template_name, {
            'service_form': service_form,
            'option_formset': option_formset,
            'schedule_formset': schedule_formset,
            'is_edit': False,
            'global_error': global_error
        })


OptionFormSet = inlineformset_factory(
    Service,
    Option,
    form=OptionForm,
    extra=0,
    can_delete=True
)

ScheduleFormSet = inlineformset_factory(
    Service,
    Schedule,
    form=ScheduleForm,
    extra=0,
    can_delete=True
)


class ProviderServiceEdit(LoginRequiredMixin, View):
    template_name = 'dashboard/services/edit.html'

    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(Service, slug=kwargs['slug'], provider_id=request.user.id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        provinces = Province.objects.all()
        selected_cities = self.service.locations.all()
        selected_city_ids = list(selected_cities.values_list('id', flat=True))
        selected_province_id = selected_cities.first().province.id if selected_cities.exists() else None

        return {
            'service_form': ServiceForm(instance=self.service),
            'option_formset': OptionFormSet(instance=self.service, prefix='option'),
            'schedule_formset': ScheduleFormSet(instance=self.service, prefix='schedule'),
            'provinces': provinces,
            'selected_cities': selected_cities,
            'selected_city_ids': selected_city_ids,
            'selected_province_id': selected_province_id,
            'is_edit': True
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': True, 'html': html})

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        service_form = ServiceForm(request.POST, request.FILES, instance=self.service)
        option_formset = OptionFormSet(request.POST, request.FILES, instance=self.service, prefix='option')
        schedule_formset = ScheduleFormSet(request.POST, request.FILES, instance=self.service, prefix='schedule')

        global_error = None
        failed_ids = []

        if service_form.is_valid() and option_formset.is_valid() and schedule_formset.is_valid():
            service = service_form.save()
            city_ids = [int(cid) for cid in request.POST.get("cities", "").split(",") if cid]
            service.locations.set(city_ids)

            # حذف آیتم‌های حذف‌شده
            for deleted in getattr(option_formset, 'deleted_objects', []):
                try:
                    deleted.delete()
                except ProtectedError:
                    global_error = "برخی آپشن‌ها به دلیل استفاده در سفارشات حذف نشدند."
                    failed_ids.append(deleted.pk)

            for deleted in getattr(schedule_formset, 'deleted_objects', []):
                try:
                    deleted.delete()
                except ProtectedError:
                    global_error = "برخی زمان‌بندی‌ها به دلیل استفاده در سفارشات حذف نشدند."
                    failed_ids.append(deleted.pk)

            # ذخیره آیتم‌های جدید/ویرایش‌شده
            for opt in option_formset.save(commit=False):
                if not getattr(opt, 'title', '').strip():
                    continue
                opt.service = service
                opt.save()

            for schedule in schedule_formset.save(commit=False):
                if not getattr(schedule, 'date', None):
                    continue
                schedule.service = service
                schedule.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if global_error:
                    errors_html = render_to_string(
                        'dashboard/services/errors.html',
                        {
                            'service_form': service_form,
                            'option_formset': option_formset,
                            'schedule_formset': schedule_formset,
                            'global_error': global_error
                        },
                        request=request
                    )
                    return JsonResponse({
                        'success': False,
                        'errors_html': errors_html,
                        'failed_ids': failed_ids
                    })
                return JsonResponse({'success': True, 'redirect_url': reverse("provider_service_list")})

            if not global_error:
                return redirect("provider_service_list")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors_html = render_to_string(
                'dashboard/services/errors.html',
                {
                    'service_form': service_form,
                    'option_formset': option_formset,
                    'schedule_formset': schedule_formset,
                    'global_error': global_error
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'errors_html': errors_html,
                'failed_ids': failed_ids
            })

        return render(request, self.template_name, {
            'service_form': service_form,
            'option_formset': option_formset,
            'schedule_formset': schedule_formset,
            'is_edit': True,
            'global_error': global_error
        })


@login_required
def load_cities(request):
    province_id = request.GET.get('province')
    if not province_id or not province_id.isdigit():
        return JsonResponse({"cities": []})
    cities = City.objects.filter(province_id=int(province_id)).order_by('name_fa')
    return JsonResponse({"cities": list(cities.values("id", "name_fa"))})


@login_required
def dashboard_services_partial(request):
    provider = get_object_or_404(Provider, user=request.user)
    services = Service.objects.filter(provider_id=provider.id).order_by('created_at')
    return render(request, 'dashboard/services/list.html', {'services': services})


@require_POST
@login_required
def delete_service(request):
    service_id = request.POST.get('service_id')
    provider = get_object_or_404(Provider, user=request.user)
    if service_id:
        Service.objects.filter(provider_id=provider.id, id=service_id).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'service_id not provided'}, status=400)


@login_required
def add_option(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        prefix = request.GET.get("prefix", "option")
        index = request.GET.get("index")
        form = OptionForm(prefix=f"{prefix}-{index}")
        html = render_to_string("dashboard/services/option_form.html", {"form": form})
        return JsonResponse({"success": True, "html": html})
    return JsonResponse({"success": False, "errors": "Invalid request"})


@require_POST
@login_required
def delete_option(request, pk):
    option = get_object_or_404(Option, pk=pk, service__provider_id=request.user.id)
    try:
        option.delete()
        return JsonResponse({'success': True, 'message': 'آپشن با موفقیت حذف شد'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': f'آپشن "{option.title}" در سفارشات استفاده شده و قابل حذف نیست.'})


@login_required
def add_schedule(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        prefix = request.GET.get("prefix", "schedule")
        index = request.GET.get("index")
        form = ScheduleForm(prefix=f"{prefix}-{index}")
        html = render_to_string("dashboard/services/schedule_form.html", {"form": form})
        return JsonResponse({"success": True, "html": html})
    return JsonResponse({"success": False, "errors": "Invalid request"})


@require_POST
@login_required
def delete_schedule(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, service__provider_id=request.user.id)
    try:
        schedule.delete()
        return JsonResponse({'success': True, 'message': 'زمان‌بندی با موفقیت حذف شد'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': f' زمان‌بندی "{schedule.date}" در سفارشات استفاده شده و قابل حذف نیست.'})
