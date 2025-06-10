from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max, Min, Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from blog.models import Post, PostTag
from blog.models import Category
from config.views import apply_filters


class PostListView(ListView):
    template_name = 'blog/list.html'
    model = Post
    context_object_name = 'posts'
    ordering = ['-id']
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        latest_posts = self.object_list.first()
        user = self.request.user if self.request.user.is_authenticated else None
        context['latest_posts'] = latest_posts

        model_fields = [
            ('categories', Category.objects.filter(is_active=True)),
            ('tags', PostTag.objects.all()),
        ]

        for field_name, queryset in model_fields:
            context[field_name] = queryset

        return context

    def get_queryset(self):
        base_qs = Post.objects.annotate(visit_count=Count('visits', distinct=True))
        filtered_qs = apply_filters(self.request, base_qs)

        sort_by = self.request.GET.get('sort_by')
        match sort_by:
            case 'most_viewed':
                filtered_qs = filtered_qs.order_by('-visit_count', '-id')
            case 'newest':
                filtered_qs = filtered_qs.order_by('-id')
            case 'oldest':
                filtered_qs = filtered_qs.order_by('id')

        return filtered_qs


@staff_member_required
@require_POST
def toggle_unique_status(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.is_unique = not post.is_unique
    post.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
