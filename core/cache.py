from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from accounts.models import User

def delete_inactive_users(exp_in_min=10):
    cache_key = 'delete_inactive_users_last_run'
    last_run = cache.get(cache_key)
    now = timezone.now()

    if not last_run or (now - last_run) > timedelta(minutes=exp_in_min):
        expiry = now - timedelta(minutes=exp_in_min)
        User.objects.filter(is_verified=False, date_joined__lt=expiry).delete()
        cache.set(cache_key, now, timeout=None)
