from django.contrib import admin

from wallet.models import Wallet, WalletTransaction, WithdrawalRequest, DepositRequest, SiteWallet, PaymentGateway, PaymentTransaction, \
    CommissionRule

admin.site.register(CommissionRule)
admin.site.register(Wallet)
admin.site.register(SiteWallet)
admin.site.register(WalletTransaction)
admin.site.register(WithdrawalRequest)
admin.site.register(PaymentGateway)
admin.site.register(PaymentTransaction)
admin.site.register(DepositRequest)
