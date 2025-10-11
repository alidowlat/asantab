from decouple import config
from zeep import Client
from kavenegar import *
from django.utils import timezone
import random

from main.settings import Kavenegar_API


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


# ---------- SERVICES ----------


def send_tracking_code_sms(mobile, tracking_code):
    mobile = [mobile, ]
    try:
        api = KavenegarAPI(config("KAVENEGAR_API"))
        params = {
            'receptor': mobile,
            'template': 'order',
            'token': tracking_code,
        }
        response = api.verify_lookup(params)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_sms_order(mobile, tracking_code):
    mobile = [mobile, ]
    try:
        api = KavenegarAPI(config("KAVENEGAR_API"))
        params = {
            'receptor': mobile,
            'template': 'order',
            'token': tracking_code,
        }
        response = api.verify_lookup(params)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_otp(mobile, otp):
    mobile = [mobile, ]
    try:
        api = KavenegarAPI(config("KAVENEGAR_API"))
        params = {
            'receptor': mobile,
            'template': 'verify',
            'token': otp,
        }
        response = api.verify_lookup(params)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_otp_rest(mobile, otp):
    mobile = [mobile, ]
    try:
        api = KavenegarAPI(config("KAVENEGAR_API"))
        params = {
            'sender': '1000400090007',
            'receptor': mobile,
            'message': 'Your OTP is {}'.format(otp)
        }
        response = api.sms_send(params)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_otp_soap(mobile, otp):
    client = Client('http://api.kavenegar.com/soap/v1.asmx?WSDL')
    receptor = [mobile, ]

    empty_array_placeholder = client.get_type('ns0:ArrayOfString')
    receptors = empty_array_placeholder()
    for item in receptor:
        receptors['string'].append(item)

    api_key = Kavenegar_API
    message = 'Your OTP is {}'.format(otp)
    sender = '1000596446'
    status = 0
    status_message = ''

    result = client.service.SendSimpleByApikey(api_key, sender, message, receptor, 0, 1, status, status_message)
    print(result)
