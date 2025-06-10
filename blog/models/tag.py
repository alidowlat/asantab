from config.models import BaseTag


class PostTag(BaseTag):
    class Meta:
        db_table = "posts_tags"
        verbose_name = "Post Tag"
        verbose_name_plural = "Post Tags"