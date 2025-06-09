from django.db import models
from config.models import BaseVisit


class BlogVisit(BaseVisit):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='visits', verbose_name='پست')

    def __str__(self):
        return f'{self.post.title} / {self.ip}'

    class Meta:
        db_table = 'posts_visits'
