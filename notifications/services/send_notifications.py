from django.template.loader import render_to_string
from main.settings import EMAIL_HOST_USER
from notifications.models import NotificationType, Notification
from django.core.mail import EmailMultiAlternatives



def notify_user(user, title, message, type_key, link=None):
    notif_type, _ = NotificationType.objects.get_or_create(key=type_key, title=title)
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link,
        notif_type=notif_type
    )

def send_custom_email(subject, to_emails, template_name, context):
    html_content = render_to_string(template_name, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=html_content,
        from_email=EMAIL_HOST_USER,
        to=[to_emails] if isinstance(to_emails, str) else to_emails
    )
    email.content_subtype = "html"
    email.send()
