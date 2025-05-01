from django.http import JsonResponse
from core.otp import set_user_otp
from accounts.models import User



def resend_otp_view(request):
    phone = request.session.get('user_phone')
    if not phone:
        return JsonResponse({'status': 'no phone'}, status=400)

    user = User.objects.filter(phone_number=phone).first()
    if not user:
        return JsonResponse({'status': 'not found'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'status': 'invalid method'}, status=405)

    success = set_user_otp(user)
    if not success:
        return JsonResponse({'status': 'error'}, status=500)
    return JsonResponse({'status': 'ok'})