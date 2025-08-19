from django.contrib import admin

from wallet.models import Wallet, WalletTransaction

admin.site.register(Wallet)
admin.site.register(WalletTransaction)