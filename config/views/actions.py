from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from services.models import Favorite, Visit


def apply_filters(request, queryset):
    filters = {
        'platform__slug__in': request.GET.get('platform', '').split(','),
        'category__slug__in': request.GET.get('category', '').split(','),
        'profession__slug__in': request.GET.get('profession', '').split(','),
        'locations__name_en__in': request.GET.get('location', '').split(','),
        'tags__slug__in': request.GET.get('tag', '').split(','),
    }

    for key, value in filters.items():
        if value and value != ['']:
            queryset = queryset.filter(**{key: value})

    if request.GET.get('available') == '1':
        queryset = queryset.filter(is_active=True)

    if request.GET.get('featured') == '1':
        queryset = queryset.filter(is_unique=True)

    search = request.GET.get('s')
    if search:
        queryset = queryset.filter(title__icontains=search)

    min_price = request.GET.get('min_price')
    if min_price:
        queryset = queryset.filter(min_price__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        queryset = queryset.filter(max_price__lte=max_price)

    return queryset


@login_required
def favorite_list_partial(request):
    favorite_list = Favorite.objects.filter(user=request.user).select_related('service').order_by('-created_at')
    return render(request, 'includes/favorite_list.html', {'favorite_list': favorite_list})


@login_required
def favorite_count(request):
    count = Favorite.objects.filter(user=request.user).count()
    return JsonResponse({'count': count})


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


@require_POST
@login_required
def delete_visit(request):
    service_id = request.POST.get('service_id')
    if service_id:
        Visit.objects.filter(user=request.user, service_id=service_id).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'service_id not provided'}, status=400)


@require_POST
@login_required
def delete_all_visits(request):
    Visit.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})
