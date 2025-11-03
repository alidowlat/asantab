from django.http import JsonResponse
from core.otp import set_user_otp, send_otp
from accounts.models import User


def resend_otp_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid method'}, status=405)

    phone = request.session.get('user_phone')
    if not phone:
        return JsonResponse({'status': 'no phone'}, status=400)

    user = User.objects.filter(phone_number=phone).first()
    if not user:
        return JsonResponse({'status': 'not found'}, status=404)

    if not set_user_otp(user):
        return JsonResponse({'status': 'error'}, status=500)

    send_otp(user.phone_number, user.otp)
    return JsonResponse({'status': 'ok'})