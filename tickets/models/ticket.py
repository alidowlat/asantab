import random
import string

from django.db import models

from core import compress_image
from wallet.models import TimeStampedModel


class TicketDepartment(models.Model):
    name = models.CharField("نام دپارتمان", max_length=40, unique=True)

    class Meta:
        verbose_name = "Ticket Department"
        verbose_name_plural = "Ticket Departments"
        db_table = "ticket_departments"

    def __str__(self):
        return self.name


class Ticket(TimeStampedModel):
    STATUS_CHOICES = [
        ("open", "در حال بررسی"),
        ("assigned", "در انتظار پاسخ کارشناس"),
        ("answered", "پاسخ داده شده"),
        ("closed", "بسته شده"),
    ]
    STATUS_CLASSES = {
        "open": "bg-yellow-10 text-yellow-500 dark:text-yellow-400",
        "answered": "bg-success/10 text-success dark:bg-emerald-900/50 dark:text-emerald-300",
        "closed": "bg-gray-100 text-gray-600 dark:bg-gray-600 dark:text-gray-300",
    }

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="کاربر",
    )
    department = models.ForeignKey(
        TicketDepartment,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="دپارتمان",
    )
    subject = models.CharField("موضوع تیکت", max_length=200)
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )
    tracking_code = models.CharField(
        "شناسه پیگیری",
        max_length=15,
        unique=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        verbose_name="کارشناس مسئول",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-updated_at"]
        db_table = "tickets"

    def __str__(self):
        return f"{self.subject} - {self.user}"

    def get_status_class(self):
        return self.STATUS_CLASSES.get(self.status, "bg-gray-100 text-gray-500")

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            rand_num = ''.join(random.choices(string.digits, k=5))
            self.tracking_code = f"AT-{rand_num}"
        super().save(*args, **kwargs)


class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="تیکت",
    )
    sender = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name="ticket_messages",
        verbose_name="فرستنده",
    )
    message = models.TextField("متن پیام", blank=True, null=True)
    attachment = models.FileField(
        "فایل ضمیمه",
        upload_to="tickets/attachments/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("تاریخ ارسال", auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.attachment and self.attachment.file.content_type.startswith('image/'):
            self.attachment = compress_image(self.attachment)
        elif self.attachment and self.attachment.size > 4 * 1024 * 1024:
            raise ValueError('حداکثر حجم فایل ۴ مگابایت است.')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Ticket Message"
        verbose_name_plural = "Ticket Messages"
        ordering = ["created_at"]
        db_table = 'ticket_messages'

    def __str__(self):
        return f"پیام از {self.sender} در تیکت {self.ticket.id}"


class SupportAgent(models.Model):
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name="support_agent",
        verbose_name="کاربر"
    )
    departments = models.ManyToManyField(
        TicketDepartment,
        related_name="agents",
        verbose_name="دپارتمان‌ها"
    )

    class Meta:
        verbose_name = "Support Agent"
        verbose_name_plural = "Support Agents"
        db_table = "support_agents"

    def __str__(self):
        return f"کارشناس: {self.user.username}"
