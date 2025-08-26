from django.contrib import admin

from wallet.models import Wallet, WalletTransaction, WithdrawalRequest, DepositRequest, SiteWallet

admin.site.register(Wallet)
admin.site.register(SiteWallet)
admin.site.register(WalletTransaction)
admin.site.register(WithdrawalRequest)
admin.site.register(DepositRequest)
