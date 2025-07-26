from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_POST
from accounts.models import Provider
from services.forms import ServiceForm, ScheduleFormSet, OptionFormSet, OptionForm, ScheduleForm
from django.views.generic import CreateView, ListView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from services.models import Service, Option


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


class ProviderServiceCreate(LoginRequiredMixin, CreateView):
    model = Service
    template_name = 'dashboard/services/create.html'
    form_class = ServiceForm
    success_url = reverse_lazy('dashboard_page')

    formset_classes = {
        'schedule_formset': ScheduleFormSet,
        'option_formset': OptionFormSet,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for name, formset_class in self.formset_classes.items():
            context[name] = kwargs.get(name) or formset_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formsets = {
            name: cls(request.POST)
            for name, cls in self.formset_classes.items()
        }

        if form.is_valid() and all(fs.is_valid() for fs in formsets.values()):
            return self.form_valid(form, formsets)
        return self.form_invalid(form, formsets)

    def form_valid(self, form, formsets):
        self.object = form.save(commit=False)
        self.object.provider = self.request.user.provider
        self.object.save()

        for formset in formsets.values():
            formset.instance = self.object
            formset.save()

        return redirect(self.success_url)

    def form_invalid(self, form, formsets):
        context = self.get_context_data(form=form, **formsets)
        return self.render_to_response(context)


OptionFormSet = modelformset_factory(Option, form=OptionForm, extra=0, can_delete=True)



class ProviderServiceEdit(LoginRequiredMixin, View):
    template_name = 'dashboard/services/edit.html'

    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(Service, slug=kwargs['slug'], provider_id=request.user.id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        service_form = ServiceForm(instance=self.service)
        option_formset = OptionFormSet(queryset=self.service.options.all(), prefix='option')
        schedule_forms = [ScheduleForm(prefix=f'schedule-{i}', instance=schedule) for i, schedule in enumerate(self.service.schedules.all())]

        return render(request, self.template_name, {
            'service_form': service_form,
            'option_formset': option_formset,
            'schedule_forms': schedule_forms,
            'is_edit': True
        })

    def post(self, request, *args, **kwargs):
        service_form = ServiceForm(request.POST, request.FILES, instance=self.service)
        option_formset = OptionFormSet(request.POST, queryset=self.service.options.all(), prefix='option')

        if service_form.is_valid() and option_formset.is_valid():
            service = service_form.save()
            options = option_formset.save(commit=False)

            for opt in options:
                opt.service = service
                opt.save()

            for deleted in option_formset.deleted_objects:
                deleted.delete()

            return redirect("provider_service_list")

        return render(request, self.template_name, {
            'service_form': service_form,
            'option_formset': option_formset,
            'is_edit': True
        })




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
    Option.objects.filter(pk=pk).delete()
    return JsonResponse({'success': True})
