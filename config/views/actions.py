from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from services.models import Favorite


@login_required
def favorite_list_partial(request):
    favorite_list = Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
    return render(request, 'includes/favorite_list.html', {'favorite_list': favorite_list})


@require_POST
@login_required
def delete_favorite(request):
    service_id = request.POST.get('service_id')
    if service_id:
        Favorite.objects.filter(user=request.user, service_id=service_id).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'service_id not provided'}, status=400)


@require_POST
@login_required
def delete_all_favorites(request):
    Favorite.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})
