from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from accounts.models import Provider
from notifications.models import Notification
from orders.models import Order, OrderItem
from orders.services import OrderCalculator
from search.models import SearchQuery
from services.models import Favorite, ServiceVisit


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
def notif_list_partial(request):
    notif_list = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'includes/notif_list.html', {'notif_list': notif_list})


@login_required
def cart_partial(request):
    cart = (
        Order.objects
        .filter(user=request.user, is_paid=False)
        .prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('service', 'option', 'schedule'))
        )
        .first()
    )

    if cart and cart.items.exists():
        calc = OrderCalculator(cart)
        return render(request, 'includes/cart_partial.html', {
            'cart': cart,
            'final_price': calc.final_price(),
        })

    return render(request, 'includes/cart_partial.html', {
        'cart': None,
        'final_price': 0,
    })



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
        ServiceVisit.objects.filter(user=request.user, service_id=service_id).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'service_id not provided'}, status=400)


@require_POST
@login_required
def delete_all_visits(request):
    ServiceVisit.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})


@require_POST
@login_required
def delete_all_searches(request):
    SearchQuery.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})


@require_POST
@login_required
def read_notif(request):
    notif_id = request.POST.get('notif_id')
    notif = get_object_or_404(Notification, user=request.user, id=notif_id)
    if not notif.is_read:
        notif.is_read = True
        notif.save()
    return JsonResponse({'status': 'ok'})


@require_POST
@login_required
def read_all_notifs(request):
    Notification.objects.filter(user_id=request.user.id, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
def unread_notifications_count(request):
    count = Notification.objects.filter(user_id=request.user.id, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def order_items_count(request):
    order = Order.objects.filter(user=request.user, is_paid=False).first()
    count = order.items.count() if order else 0
    return JsonResponse({'count': count})


@login_required
def received_orders_count(request):
    provider = get_object_or_404(Provider, user=request.user)
    count = Order.objects.filter(
        provider=provider,
        is_paid=True,
        status__in=['pending', 'accepted']
    ).count()
    return JsonResponse({'count': count})
