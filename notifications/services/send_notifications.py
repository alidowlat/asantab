from notifications.models import NotificationType, Notification


def notify_user(user, title, message, type_key, link=None):
    notif_type = NotificationType.objects.filter(key=type_key).first()
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link,
        notif_type=notif_type
    )
