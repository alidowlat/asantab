from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from jalali_date import date2jalali
from accounts.models import Provider
from dashboard.forms import UpdateEmailForm, UpdateNameForm, UpdatePhoneForm, UpdateNationalIDForm, UpdateGenderForm, \
    UpdateBirthdateForm, UpdateUsernameForm, UpdateBioForm, UpdateLocationForm, UpdateProfileImageForm, UpdatePasswordForm, \
    UpdatePlatformUrlsForm, UpdateNationalCardImageForm


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/account/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_provider:
            provider = get_object_or_404(Provider, user=user)
            context['provider'] = provider
        context['email_form'] = UpdateEmailForm(instance=user)
        context['email_form'] = UpdateEmailForm(instance=user)
        context['name_form'] = UpdateNameForm(instance=user)
        context['phone_form'] = UpdatePhoneForm(instance=user)
        context['national_id_form'] = UpdateNationalIDForm(instance=user)
        context['gender_form'] = UpdateGenderForm(instance=user)

        if user.is_provider:
            context['username_form'] = UpdateUsernameForm(instance=provider)
            context['bio_form'] = UpdateBioForm(instance=provider)
            context['location_form'] = UpdateLocationForm(instance=provider)
            context['national_card_image_form'] = UpdateNationalCardImageForm(instance=provider)
            context['profile_image_form'] = UpdateProfileImageForm(instance=provider)
            context['platformurls_form'] = UpdatePlatformUrlsForm(instance=provider)
            context['password_form'] = UpdatePasswordForm(user=self.request.user)

        initial = {}
        if user.birth_date:
            jalali = date2jalali(user.birth_date)
            initial = {
                'birth_day': jalali.day,
                'birth_month': jalali.month,
                'birth_year': jalali.year,
            }
        context['birthdate_form'] = UpdateBirthdateForm(instance=user, initial=initial)

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


class UpdateUsernameView(LoginRequiredMixin, View):
    def get(self, request):
        username_form = UpdateUsernameForm(instance=request.user)
        return render(request, 'dashboard/account/modal/username_modal.html', {'username_form': username_form})

    def post(self, request):
        if not request.user.is_provider:
            return JsonResponse({'success': False})

        provider = get_object_or_404(Provider, user=request.user)
        form = UpdateUsernameForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})
        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateBioView(LoginRequiredMixin, View):
    def get(self, request):
        bio_form = UpdateBioForm(instance=request.user)
        return render(request, 'dashboard/account/modal/bio_modal.html', {'bio_form': bio_form})

    def post(self, request):
        if not request.user.is_provider:
            return JsonResponse({'success': False})

        provider = get_object_or_404(Provider, user=request.user)
        form = UpdateBioForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateLocationView(LoginRequiredMixin, View):
    def get(self, request):
        location_form = UpdateLocationForm(instance=request.user)
        return render(request, 'dashboard/account/modal/location_modal.html', {'location_form': location_form})

    def post(self, request):
        if not request.user.is_provider:
            return JsonResponse({'success': False})

        provider = get_object_or_404(Provider, user=request.user)
        form = UpdateLocationForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateNationalCardImageView(LoginRequiredMixin, View):
    def get(self, request):
        national_card_image_form = UpdateNationalCardImageForm(instance=request.user)
        return render(request, 'dashboard/account/modal/national_card_image_modal.html',
                      {'national_card_image_form': national_card_image_form})

    def post(self, request):
        if not request.user.is_provider:
            return JsonResponse({'success': False})

        provider = get_object_or_404(Provider, user=request.user)
        form = UpdateNationalCardImageForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdateProfileImageView(LoginRequiredMixin, View):
    def get(self, request):
        profile_image_form = UpdateProfileImageForm(instance=request.user)
        return render(request, 'dashboard/account/modal/profile_image_modal.html', {'profile_image_form': profile_image_form})

    def post(self, request):
        if not request.user.is_provider:
            return JsonResponse({'success': False})

        provider = get_object_or_404(Provider, user=request.user)
        form = UpdateProfileImageForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdatePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        password_form = UpdatePasswordForm(user=request.user)
        return render(request, 'dashboard/account/modal/password_modal.html', {'password_form': password_form})

    def post(self, request):
        if not request.user.is_provider:
            return JsonResponse({'success': False})

        user = request.user
        has_password = user.has_usable_password()

        form = UpdatePasswordForm(request.POST, user=user)

        if form.is_valid():
            if has_password:
                old_password = form.cleaned_data.get('old_password')
                if not user.check_password(old_password):
                    form.add_error('old_password', 'کلمه عبور فعلی وارد شده اشتباه است.')
                    return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})

            user.set_password(form.cleaned_data.get('new_password'))
            user.save()
            update_session_auth_hash(request, user)

            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})

        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})


class UpdatePlatformUrlsView(LoginRequiredMixin, View):
    def get(self, request):
        platformurls_form = UpdatePlatformUrlsForm(instance=request.user)
        return render(request, 'dashboard/account/modal/platform_modal.html', {'platformurls_form': platformurls_form})

    def post(self, request):
        if not request.user.is_provider:
            return JsonResponse({'success': False})

        provider = get_object_or_404(Provider, user=request.user)
        form = UpdatePlatformUrlsForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('account_info_page')})
        return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})
