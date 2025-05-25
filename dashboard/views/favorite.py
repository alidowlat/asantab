from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView
from services.models import Favorite


class FavoriteListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/favorite/main.html'
    context_object_name = 'favorite_list'
    model = Favorite

    def get_context_data(self, **kwargs):
        context = super(FavoriteListView, self).get_context_data(**kwargs)
        request = self.request
        context['favorite_list'] = (
            Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
        )

        return context


def dashboard_favorite_list_partial(LoginRequiredMixin, request):
    favorite_list = Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
    return render(request, 'dashboard/favorite/list.html', {'favorite_list': favorite_list})
