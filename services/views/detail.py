from django.db.models import Q, Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from reviews.forms import ServiceReviewForm
from reviews.models.service_review import ServiceReview, ServiceReviewReaction
from services.models import Service


class ServiceDetailView(DetailView):
    template_name = 'services/detail.html'
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_service = self.object

        prices = list(loaded_service.options.filter(unit_price__isnull=False).values_list('unit_price', flat=True))
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        context['min_price'] = min_price
        context['max_price'] = max_price

        related_services = Service.objects.filter(
            Q(profession__in=loaded_service.profession.all()) |
            Q(tags__in=loaded_service.tags.all())
        ).exclude(id=loaded_service.id).distinct()
        context['related_services'] = related_services

        service_reviews = ServiceReview.objects.filter(service_id=loaded_service.id, status='approved').select_related(
            'user').annotate(
            like_count=Count('reactions', filter=Q(reactions__reaction='like')),
            dislike_count=Count('reactions', filter=Q(reactions__reaction='dislike'))
        ).order_by('-created_at')
        context['service_reviews'] = service_reviews

        last_review = ServiceReview.objects.filter(service_id=loaded_service.id, status='approved').select_related('user').annotate(
            like_count=Count('reactions', filter=Q(reactions__reaction='like')),
            dislike_count=Count('reactions', filter=Q(reactions__reaction='dislike'))
        ).order_by('-created_at').first()
        context['last_review'] = last_review

        reviews_count = ServiceReview.objects.filter(service_id=loaded_service.id, status='approved').select_related('user').count()
        context['reviews_count'] = reviews_count

        if self.request.user.is_authenticated:
            liked_ids = set(
                ServiceReviewReaction.objects.filter(user=self.request.user, reaction='like').values_list('review_id', flat=True)
            )
            disliked_ids = set(
                ServiceReviewReaction.objects.filter(user=self.request.user, reaction='dislike').values_list('review_id', flat=True)
            )
        else:
            liked_ids = set()
            disliked_ids = set()

        context['liked_ids'] = liked_ids
        context['disliked_ids'] = disliked_ids

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
def toggle_reaction(request):
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
