from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import render
from accounts.models import Provider
from blog.models import Post
from search.models import SearchQuery
from services.models import Service


def search_view(request):
    query = request.GET.get('search', '').strip()

    results = {
        'posts': [],
        'services': [],
        'providers': []
    }

    if query and len(query) >= 2:
        results['posts'] = Post.objects.filter(title__icontains=query)[:7]
        results['services'] = Service.objects.filter(title__icontains=query)[:7]
        results['providers'] = (
            Provider.objects
            .select_related('user')
            .annotate(full_name=Concat('user__first_name', Value(' '), 'user__last_name'))
            .filter(Q(username__icontains=query) | Q(full_name__icontains=query))
            .order_by('-id')[:7]
        )

        SearchQuery.objects.create(
            query=query[:255],
            user=request.user if request.user.is_authenticated else None
        )

    return render(request, 'search/components/search_result.html', {'results': results})
