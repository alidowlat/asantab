from django.utils import timezone
import random


def get_random_otp(length=5):
    return ''.join(random.choices('0123456789', k=length))


def set_user_otp(user):
    otp = get_random_otp()
    user.otp = otp
    user.otp_create_at = timezone.now()
    user.save(update_fields=['otp', 'otp_create_at'])
    return otp


def is_otp_expired(user, expiry_seconds=180):
    if not user.otp_create_at:
        return True
    diff = timezone.now() - user.otp_create_at
    return diff.total_seconds() > expiry_seconds


def is_valid_otp(user, input_otp):
    return not is_otp_expired(user) and user.otp == input_otp
