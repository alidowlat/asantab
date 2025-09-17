import requests
from wallet.models import DepositRequest, PaymentGateway


class DepositService:
    @staticmethod
    def create_deposit(user, amount, description="شارژ کیف پول از طریق آقای پرداخت"):
        gateway = PaymentGateway.objects.first()
        deposit = DepositRequest.objects.create(
            wallet=user.wallet,
            amount=amount,
            gateway=gateway,
            description=description
        )
        print(">>> Deposit created:", deposit.id, deposit.amount)
        return deposit

    @staticmethod
    def start_payment(deposit: DepositRequest):
        url = "https://panel.aqayepardakht.ir/api/v2/create"
        data = {
            "pin": 'sandbox',
            "amount": int(deposit.amount),
            "callback": "http://localhost:8000/wallet/deposit/verify/",
            "invoice_id": str(deposit.id),
            "description": deposit.description,
            "mobile": getattr(deposit.wallet.user, "phone_number", ""),
        }
        print(">>> Sending request to gateway with data:", data)

        try:
            resp = requests.post(url, json=data, timeout=10)
            print(">>> Gateway raw response:", resp.status_code, resp.text)
            resp = resp.json()
        except Exception as e:
            print(">>> ERROR in request:", e)
            deposit.mark_failed()
            return None
        print(">>> Parsed response JSON:", resp)

        if resp.get("status") == "success":
            deposit.ref_id = str(resp["transid"])
            deposit.save(update_fields=["ref_id"])
            dep_check = DepositRequest.objects.get(pk=deposit.pk)
            print(">>> Saved ref_id in DB:", dep_check.ref_id)
            return f"https://panel.aqayepardakht.ir/startpay/sandbox/{resp['transid']}"
        else:
            print(">>> Gateway returned failure:", resp)
            deposit.mark_failed()
            return None

    @staticmethod
    def verify_payment(transid, amount):
        url = "https://panel.aqayepardakht.ir/api/v2/verify"
        data = {
            "pin": 'sandbox',
            "amount": int(amount),
            "transid": transid
        }
        resp = requests.post(url, json=data, timeout=10).json()
        if resp.get("code") == "1":
            return True
        return False