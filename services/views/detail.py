from django.db.models import Q, Count, Min, Max
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from core import get_client_info
from reviews.models.service_review import ServiceReview, ServiceReviewReaction
from services.models import Service, Visit


class ServiceDetailView(DetailView):
    template_name = 'services/detail.html'
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_service = self.object
        user = self.request.user if self.request.user.is_authenticated else None

        price_range = loaded_service.options.aggregate(
            min_price=Min('unit_price'), max_price=Max('unit_price')
        )
        context['min_price'] = price_range['min_price']
        context['max_price'] = price_range['max_price']

        related_services = Service.objects.filter(
            Q(profession__in=loaded_service.profession.all()) |
            Q(tags__in=loaded_service.tags.all())
        ).exclude(id=loaded_service.id).distinct()
        context['related_services'] = related_services

        base_reviews_qs = ServiceReview.objects.filter(
            service_id=loaded_service.id, status='approved'
        ).select_related('user')

        annotated_reviews = base_reviews_qs.annotate(
            like_count=Count('reactions', filter=Q(reactions__reaction='like')),
            dislike_count=Count('reactions', filter=Q(reactions__reaction='dislike'))
        ).order_by('-created_at')

        context['service_reviews'] = annotated_reviews
        context['last_review'] = annotated_reviews.first()
        context['reviews_count'] = base_reviews_qs.count()

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

        ip, user_agent, referer = get_client_info(self.request)

        visit_exists = Visit.objects.filter(ip=ip, service=loaded_service).exists()
        if not visit_exists:
            Visit.objects.create(
                service=loaded_service,
                ip=ip,
                user=user,
                user_agent=user_agent,
                referer=referer
            )

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
