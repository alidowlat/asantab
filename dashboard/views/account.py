from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class AccountView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'user': request.user,
        }
        return render(request, 'dashboard/account/main.html', context)

    def post(self, request):
        pass