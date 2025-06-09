from django.db.models import Q, Count
from django.views.generic import DetailView
from blog.models import Post, BlogVisit, Category
from core import get_client_info
from core.clean import create_visit_clean


class BlogDetailView(DetailView):
    template_name = 'blog/detail.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_post = self.object
        user = self.request.user if self.request.user.is_authenticated else None

        related_posts = (
            Post.objects
            .filter(Q(category=loaded_post.category))
            .exclude(id=loaded_post.id)
            .distinct()
        )
        context['related_posts'] = related_posts

        most_viewed_posts = (
            Post.objects
            .filter(is_active=True)
            .exclude(pk=loaded_post.pk)
            .annotate(view_count=Count('visits'))
            .order_by('-view_count')[:4]
        )
        context['most_viewed_posts'] = most_viewed_posts

        categories = (
            Category.objects
            .filter(is_active=True)
            .annotate(active_posts_count=Count('posts', filter=Q(posts__is_active=True)))
        )
        context['categories'] = categories

        create_visit_clean(
            user=self.request.user,
            model=BlogVisit,
            request=self.request,
            fk_name='post',
            http_service=get_client_info,
            loaded_obj=loaded_post,
        )

        return context
