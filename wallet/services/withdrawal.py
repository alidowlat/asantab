import requests

from wallet.models import WithdrawalRequest


class WithdrawService:
    @staticmethod
    def create_withdraw(user, amount, bank_account, description="برداشت از کیف پول"):
        withdraw = WithdrawalRequest.objects.create(
            wallet=user.wallet,
            amount=amount,
            bank_account=bank_account,
            description=description
        )
        print(">>> Withdraw created:", withdraw.id, withdraw.amount)
        return withdraw

    @staticmethod
    def start_withdraw(withdraw: WithdrawalRequest):
        url = "https://panel.aqayepardakht.ir/api/v2/withdraw/request"
        data = {
            "account": withdraw.card_number or "",
            "code": getattr(withdraw.wallet, "secret_code", ""),
            "amount": int(withdraw.amount),
            "iban": withdraw.sheba_number or "",
            "pin": "sandbox",
        }
        print(">>> Sending request to gateway with data:", data)

        try:
            resp = requests.post(url, json=data, timeout=10)
            print(">>> Gateway raw response:", resp.status_code, resp.text)
            resp = resp.json()
        except Exception as e:
            print(">>> ERROR in request:", e)
            withdraw.mark_rejected()
            return None
        print(">>> Parsed response JSON:", resp)

        if resp.get("status") == "success":
            withdraw.ref_id = str(resp["transid"])
            withdraw.save(update_fields=["ref_id"])
            check_withdraw = WithdrawalRequest.objects.get(pk=withdraw.pk)
            print(">>> Saved ref_id in DB:", check_withdraw.ref_id)
            return True
        else:
            print(">>> Gateway returned failure:", resp)
            withdraw.mark_rejected()
            return False

    @staticmethod
    def verify_withdraw(transid, amount):
        url = "https://panel.aqayepardakht.ir/api/v2/verify_withdraw"
        data = {
            "pin": 'sandbox',
            "amount": int(amount),
            "transid": transid
        }
        resp = requests.post(url, json=data, timeout=10).json()
        if resp.get("code") == "1":
            return True
        return False
