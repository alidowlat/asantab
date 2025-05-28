from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from dashboard.forms import UpdateEmailForm, UpdateNameForm, UpdatePhoneForm, UpdateNationalIDForm, UpdateGenderForm, \
    UpdateBirthdateForm


# class AccountView(LoginRequiredMixin, View):
#     def get(self, request):
#         return render(request, 'dashboard/account/main.html', {})


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/account/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['email_form'] = UpdateEmailForm(instance=user)
        context['name_form'] = UpdateNameForm(instance=user)
        context['phone_form'] = UpdatePhoneForm(instance=user)
        context['national_id_form'] = UpdateNationalIDForm(instance=user)
        context['gender_form'] = UpdateGenderForm(instance=user)
        context['birthdate_form'] = UpdateBirthdateForm(instance=user)

        return context


class UpdateEmailView(LoginRequiredMixin, View):
    def get(self, request):
        email_form = UpdateEmailForm(instance=request.user)
        return render(request, 'dashboard/account/modal/email_modal.html', {'email_form': email_form})

    def post(self, request):
        form = UpdateEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateNameView(LoginRequiredMixin, View):
    def get(self, request):
        name_form = UpdateNameForm(instance=request.user)
        return render(request, 'dashboard/account/modal/name_modal.html', {'name_form': name_form})

    def post(self, request):
        form = UpdateNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdatePhoneView(LoginRequiredMixin, View):
    def get(self, request):
        phone_form = UpdatePhoneForm(instance=request.user)
        return render(request, 'dashboard/account/modal/phone_modal.html', {'phone_form': phone_form})

    def post(self, request):
        form = UpdatePhoneForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateNationalIDView(LoginRequiredMixin, View):
    def get(self, request):
        national_id_form = UpdateNationalIDForm(instance=request.user)
        return render(request, 'dashboard/account/modal/national_id_modal.html', {'national_id_form': national_id_form})

    def post(self, request):
        if request.user.national_id:
            return JsonResponse({
                'success': False,
                'error': 'شما قبلاً کد ملی ثبت کرده‌اید.',
                'type': 'already_submitted'
            }, status=403)

        form = UpdateNationalIDForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateGenderView(LoginRequiredMixin, View):
    def get(self, request):
        gender_form = UpdateGenderForm(instance=request.user)
        return render(request, 'dashboard/account/modal/gender_modal.html', {'gender_form': gender_form})

    def post(self, request):
        form = UpdateGenderForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateBirthdateView(LoginRequiredMixin, View):
    def get(self, request):
        birthdate_form = UpdateBirthdateForm(instance=request.user)
        return render(request, 'dashboard/account/modal/birthdate_modal.html', {'birthdate_form': birthdate_form})

    def post(self, request):
        form = UpdateBirthdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})
