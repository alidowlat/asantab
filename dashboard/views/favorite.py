from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from services.models import Favorite


@method_decorator(login_required, name='dispatch')
class FavoriteListView(ListView):
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


@login_required
def dashboard_favorite_list_partial(request):
    favorite_list = Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
    return render(request, 'dashboard/favorite/list.html', {'favorite_list': favorite_list})
