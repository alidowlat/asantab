from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, F
from django.http import HttpResponseForbidden, Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView
from accounts.models import Provider
from core import ActiveProviderRequiredMixin
from dashboard.forms import OrderContentForm
from notifications.services import notify_user
from orders.models import Order, OrderItem, VendorOrder, OrderContentFile, OrderContent
from orders.services import OrderCalculator
from orders.models import STATUS_CHOICES
from services.models import Schedule
from wallet.models import WalletTransaction, CommissionRule, SiteWallet


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/order/main.html'
    model = Order

    def get_orders(self, is_paid, select_fields=None, status=None):
        qs = Order.objects.filter(user=self.request.user, is_paid=is_paid)
        if status:
            qs = qs.filter(status=status)
        if select_fields:
            qs = qs.prefetch_related(
                Prefetch('items', queryset=OrderItem.objects.select_related(*select_fields))
            )
        else:
            qs = qs.prefetch_related('items')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_items = self.get_orders(False, ['service', 'option', 'schedule']).order_by('-created_at')
        order_items = self.get_orders(True, ['service']).order_by('-paid_at')

        context.update({
            "cart_items": cart_items,
            "order_items": order_items,
            "pending_orders": order_items.filter(status="pending"),
            "accepted_orders": order_items.filter(status="accepted"),
            "completed_orders": order_items.filter(status="completed"),
            "rejected_orders": order_items.filter(status="rejected"),
        })

        for status_value, _ in STATUS_CHOICES:
            context[f'order_{status_value}'] = self.get_orders(True, ['service'], status_value)

        return context


class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/order/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs.get('pk')

        order = (
            Order.objects
            .filter(pk=order_pk, user=self.request.user, is_paid=True)
            .prefetch_related(
                Prefetch(
                    'vendor_orders',
                    queryset=VendorOrder.objects.prefetch_related(
                        Prefetch(
                            'items',
                            queryset=OrderItem.objects.select_related('service', 'option', 'schedule')
                        )
                    )
                )
            )
            .first()
        )

        if not order:
            raise Http404("سفارشی برای شما پیدا نشد.")

        calc = OrderCalculator(order)

        context['loaded_order'] = order
        context['vendor_orders'] = order.vendor_orders.all()
        context['discount_amount'] = calc.discount_amount()
        context['final_price'] = calc.final_price()
        return context


class OrderContentCreateView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

        content = OrderContent.objects.filter(order_item=item).exists()
        if content:
            return redirect('order_detail', pk=item.order.pk)

        form = OrderContentForm()
        context = {
            'form': form,
            'item': item,
        }
        return render(request, 'dashboard/order/order_item_content_form.html', context)

    def post(self, request, item_id):
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

        content = OrderContent.objects.filter(order_item=item).exists()
        if content:
            return redirect('order_detail', pk=item.order.pk)

        form = OrderContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.order_item = item
            content.save()

            files = request.FILES.getlist('files[]')

            for f in files:
                OrderContentFile.objects.create(content=content, file=f)

            return redirect('order_detail', pk=item.order.pk)

        context = {
            'form': form,
            'item': item,
        }
        return render(request, 'dashboard/order/order_item_content_form.html', context)


class OrderContentDetailView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        content = get_object_or_404(OrderContent, order_item=item)
        files = content.files.all()

        context = {
            'item': item,
            'content': content,
            'files': files,
        }
        return render(request, 'dashboard/order/order_item_content_detail.html', context)


class ProviderOrderListView(LoginRequiredMixin, ActiveProviderRequiredMixin, ListView):
    template_name = 'dashboard/order/provider/main.html'
    model = VendorOrder
    context_object_name = 'vendor_orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def get_vendor_orders(status=None):
            provider = get_object_or_404(Provider, user=self.request.user)
            queryset = VendorOrder.objects.filter(provider=provider).order_by('-created_at')
            if status:
                queryset = queryset.filter(status=status)
            queryset = queryset.prefetch_related(
                Prefetch('items', queryset=OrderItem.objects.select_related('service'))
            )
            return queryset

        vendor_orders = get_vendor_orders()

        context['vendor_orders'] = vendor_orders

        for status_value, _ in STATUS_CHOICES:
            context[f'order_{status_value}'] = get_vendor_orders(status_value)

        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        provider = get_object_or_404(Provider, user=user)

        if not user.is_provider or not provider:
            return HttpResponseForbidden("شما دسترسی به این بخش ندارید.")

        if not provider.is_profile_complete and provider.status == 'active':
            messages.warning(request, "برای مشاهده سفارش‌ها، لطفاً اطلاعات حساب خود را کامل کنید.")
            return redirect('dashboard_page')

        return super().dispatch(request, *args, **kwargs)


class ProviderOrderDetailView(LoginRequiredMixin, ActiveProviderRequiredMixin, DetailView):
    template_name = 'dashboard/order/provider/order_detail.html'
    model = VendorOrder
    context_object_name = 'vendor_order'

    def get_queryset(self):
        provider = get_object_or_404(Provider, user=self.request.user)
        return (
            VendorOrder.objects
            .filter(provider=provider)
            .select_related('order', 'provider')
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=OrderItem.objects.select_related('service', 'option', 'schedule')
                )
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get("action")

        if action == "complete":
            self.object.status = "completed"
            self.object.save(update_fields=["status"])

            order = self.object.order
            user = order.user

            notify_user(
                user=user,
                title="تکمیل سفارش شما",
                message=f"سفارش شما با شماره {order.id} توسط ارائه‌دهنده با موفقیت تکمیل شد.",
                type_key="order_completed",
                link=reverse("order_detail", kwargs={"pk": order.pk}),
            )

        return redirect("received_order_detail", pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor_order"] = self.object
        return context


class ProviderOrderContentDetailView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        item = get_object_or_404(
            OrderItem,
            id=item_id,
            vendor_order__provider=request.user.providers
        )

        content = get_object_or_404(OrderContent, order_item=item)
        files = content.files.all()

        context = {
            'item': item,
            'content': content,
            'files': files,
        }
        return render(request, 'dashboard/order/order_item_content_detail.html', context)



def _accept_vendor_order(vendor_order, order, buyer_wallet, seller_wallet, site_wallet):
    """
    قبول سفارش توسط فروشنده:
    - انتقال مبلغ از frozen/buyer به ولت سایت و ولت فروشنده (ثبت تراکنش‌ها)
    - تغییر وضعیت vendor_order -> accepted
    (توجه: این تابع ظرفیت را کم نمی‌کند؛ فرض می‌کنیم ظرفیت هنگام checkout کسر شده است.)
    """
    total_price = vendor_order.total_price
    commission_rule = CommissionRule.objects.first()
    commission = commission_rule.calculate(total_price) if commission_rule else Decimal("0")
    seller_income = Decimal(total_price) - Decimal(commission)

    buyer_wallet.balance -= total_price
    buyer_wallet.frozen_balance -= total_price
    buyer_wallet.save(update_fields=["balance", "frozen_balance"])

    WalletTransaction.objects.create(
        wallet=buyer_wallet,
        amount=-total_price,
        type="transfer",
        description=f"سفارش {order.tracking_code} - پرداخت کامل شد",
    )

    if site_wallet:
        site_wallet.balance = F('balance') + commission
        site_wallet.save(update_fields=["balance"])
        WalletTransaction.objects.create(
            wallet=site_wallet,
            amount=commission,
            type="deposit",
            description=f"سود از سفارش {order.tracking_code}",
        )

    seller_wallet.balance += seller_income
    seller_wallet.save(update_fields=["balance"])

    WalletTransaction.objects.create(
        wallet=seller_wallet,
        amount=seller_income,
        type="deposit",
        description=f"سفارش {order.tracking_code} - واریز پس از کسر کارمزد",
    )

    if commission > 0:
        WalletTransaction.objects.create(
            wallet=seller_wallet,
            amount=-commission,
            type="commission",
            description=f"سفارش {order.tracking_code} - کسر کارمزد {commission} تومان",
        )

    vendor_order.status = "accepted"
    vendor_order.rejection_reason = None
    vendor_order.save(update_fields=["status", "rejection_reason"])

    return {"status": "success", "message": "سفارش تایید شد و مبلغ پس از کسر کارمزد منتقل گردید."}


def _reject_vendor_order(vendor_order, order, buyer_wallet, rejection_reason=""):
    """
    رد سفارش توسط فروشنده:
    - بازگرداندن ظرفیت به schedule (افزایش capacity به اندازهٔ item.count)
    - بازگرداندن مبلغ به کیف پول خریدار (frozen -> balance)
    - ثبت تراکنش release
    - تنظیم وضعیت vendor_order = rejected و ذخیره reason
    """
    # بازگرداندن ظرفیت (atomic update با F)
    for item in vendor_order.items.select_related("schedule").all():
        if item.schedule:
            # استفاده از update با F تا همزمانی بهتر مدیریت شود
            Schedule.objects.filter(pk=item.schedule.pk).update(capacity=F("capacity") + item.count)

    # برگرداندن مبلغ به خریدار
    buyer_wallet.frozen_balance -= vendor_order.total_price
    buyer_wallet.balance += vendor_order.total_price
    buyer_wallet.save(update_fields=["balance", "frozen_balance"])

    WalletTransaction.objects.create(
        wallet=buyer_wallet,
        amount=vendor_order.total_price,
        type="release",
        description=f"سفارش {order.tracking_code} - رد شد، مبلغ آزاد شد",
    )

    vendor_order.status = "rejected"
    vendor_order.rejection_reason = rejection_reason or ""
    vendor_order.save(update_fields=["status", "rejection_reason"])

    return {"status": "warning", "message": "سفارش رد شد و مبلغ آزاد گردید."}


def handle_vendor_order_response(vendor_order, accepted: bool, rejection_reason: str = None):
    """
    wrapper: تمام عملیات درون تراکنش انجام میشه
    توجه: اگر منطق پروژه‌ت اینه که ظرفیت هنگام checkout کسر میشه،
    این توابع به خوبی با هم کار می‌کنند (accept فقط وضعیت و تراکنش‌ها رو مدیریت می‌کنه،
    reject ظرفیت را مجدداً برمی‌گرداند).
    """
    order = vendor_order.order
    buyer = order.user
    buyer_wallet = buyer.wallet
    seller = vendor_order.provider.user
    seller_wallet = seller.wallet
    site_wallet_obj = SiteWallet.objects.select_related("wallet").first()
    site_wallet = site_wallet_obj.wallet if site_wallet_obj else None

    with transaction.atomic():
        if accepted:
            result = _accept_vendor_order(vendor_order, order, buyer_wallet, seller_wallet, site_wallet)

            notify_user(
                user=buyer,
                title="سفارش شما تأیید شد",
                message=f"سفارش مربوطه توسط ارائه‌دهنده تأیید شد.",
                type_key="order_accepted",
                link=reverse('order_detail', args=[order.id])
            )

            notify_user(
                user=seller,
                title="تأیید سفارش",
                message=f"شما سفارش کاربر {buyer.get_full_name() or buyer.phone_number} را تأیید کردید.",
                type_key="vendor_order_accepted",
                link=reverse('received_order_detail', args=[vendor_order.id])
            )

            return result
        else:
            result = _reject_vendor_order(vendor_order, order, buyer_wallet, rejection_reason=rejection_reason)

            notify_user(
                user=buyer,
                title="سفارش شما رد شد ❌",
                message=f"سفارش مربوطه توسط ارائه‌دهنده رد شد."
                        + (f" دلیل: {rejection_reason}" if rejection_reason else ""),
                type_key="order_rejected",
                link=reverse('order_detail', args=[order.id])
            )

            notify_user(
                user=seller,
                title="رد سفارش ثبت شد",
                message=f"شما سفارش کاربر {buyer.get_full_name() or buyer.phone_number} را رد کردید.",
                type_key="vendor_order_rejected",
                link=reverse('vendor_order_detail', args=[vendor_order.id])
            )

            return result


@require_POST
def vendor_order_action(request, pk, action):
    vendor_order = get_object_or_404(VendorOrder, pk=pk, provider__user=request.user)

    if action == "accept":
        data = handle_vendor_order_response(vendor_order, accepted=True)

    elif action == "reject":
        reason = request.POST.get("rejection_reason", "").strip()
        if not reason:
            return JsonResponse({"status": "error", "message": "لطفاً دلیل رد سفارش را وارد کنید."})
        data = handle_vendor_order_response(vendor_order, accepted=False, rejection_reason=reason)

    else:
        data = {"status": "error", "message": "عملیات نامعتبر است."}

    return JsonResponse(data)
