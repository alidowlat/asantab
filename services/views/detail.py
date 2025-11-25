from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from accounts.models import Provider
from core import get_client_info
from core.clean import create_visit_clean
from reviews.models.service_review import ServiceReview, ServiceReviewReaction
from services.helper import ServiceDataFetcher
from services.models import Service, ServiceVisit, Favorite
from services.services import extract_instagram_data, get_instagram_data


class ServiceDetailView(DetailView):
    template_name = 'services/detail.html'
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object
        user = self.request.user if self.request.user.is_authenticated else None

        fetcher = ServiceDataFetcher(service)

        # min and max price
        price_range = fetcher.get_price_range()
        context['min_price'] = price_range['min_price']
        context['max_price'] = price_range['max_price']

        # instagram api
        context['ig_data'] = extract_instagram_data(service.platform_link)

        # related services
        context['related_services'] = fetcher.get_related_services()

        # schedules
        context['schedules'] = fetcher.get_schedules()

        # reviews
        reviews, reviews_count = fetcher.get_annotated_reviews()
        context['service_reviews'] = reviews
        context['last_review'] = reviews.first()
        context['reviews_count'] = reviews_count

        # favorites
        context['is_favorite'] = Favorite.objects.filter(service=service, user=user).exists() if user else False

        # likes and dislikes
        context['liked_ids'], context['disliked_ids'] = self.get_review_reactions()

        # create visit
        create_visit_clean(
            user=self.request.user,
            model=ServiceVisit,
            request=self.request,
            fk_name='service',
            http_service=get_client_info,
            loaded_obj=service,
        )

        return context

    def get_review_reactions(self):
        user = self.request.user
        if not user.is_authenticated:
            return set(), set()

        liked_ids = set(ServiceReviewReaction.objects.filter(
            user=user, reaction='like').values_list('review_id', flat=True))
        disliked_ids = set(ServiceReviewReaction.objects.filter(
            user=user, reaction='dislike').values_list('review_id', flat=True))

        return liked_ids, disliked_ids


def get_ig_data_api(request, username):
    data = get_instagram_data(username)
    return JsonResponse(data or {})


class ProviderDetailView(DetailView):
    model = Provider
    template_name = "providers/detail.html"
    context_object_name = "provider"

    def get_context_data(self, **kwargs):
        context = super(ProviderDetailView, self).get_context_data(**kwargs)
        related_services = Service.objects.filter(
            is_active=True,
            provider=self.object
        ).select_related('provider')
        context['related_services'] = related_services

        return context


def add_service_review(request: HttpRequest):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'ابتدا وارد حساب کاربری شوید.'}, status=401)

    service_id = request.POST.get('service_id')
    text = request.POST.get('text')
    title = request.POST.get('title')
    recommendation = request.POST.get('recommendation')

    if not service_id:
        return JsonResponse({'error': 'اطلاعات ناقص است'}, status=400)

    new_review = ServiceReview(
        user_id=request.user.id,
        service_id=service_id,
        title=title,
        text=text,
        recommendation=recommendation,
        status='pending'
    )
    new_review.save()

    html = render_to_string('services/components/service_review.html', {}, request=request)
    return JsonResponse({
        'success': True,
        'html': html
    })


@require_POST
def toggle_reaction_service(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'برای انجام این عملیات باید وارد حساب شوید.'}, status=403)

    review_id = request.POST.get('review_id')
    reaction_type = request.POST.get('reaction')

    review = get_object_or_404(ServiceReview, id=review_id)
    reaction, created = ServiceReviewReaction.objects.get_or_create(
        user=request.user,
        review=review,
        defaults={'reaction': reaction_type}
    )

    if not created:
        if reaction.reaction == reaction_type:
            reaction.delete()
            status = 'removed'
        else:
            reaction.reaction = reaction_type
            reaction.save()
            status = 'updated'
    else:
        status = 'created'

    like_count = review.reactions.filter(reaction='like').count()
    dislike_count = review.reactions.filter(reaction='dislike').count()

    return JsonResponse({
        'status': status,
        'like_count': like_count,
        'dislike_count': dislike_count
    })


@require_POST
def toggle_favorite_service(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'برای انجام این عملیات باید وارد حساب شوید.'}, status=403)

    service_id = request.POST.get('service_id')
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'service_not_found'}, status=404)

    user = request.user
    favorite, created = Favorite.objects.get_or_create(user=user, service=service)

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})
