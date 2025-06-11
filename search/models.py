from django.db import models


class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
        ]
        db_table = 'search'

    def __str__(self):
        return self.query