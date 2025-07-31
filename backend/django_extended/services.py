from django.conf import settings
from django.core.mail import send_mail


def send_email_after_registration(user_email: str) -> None:
    send_mail(
        subject="E-WALLET!",
        message="Registration Notification",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        html_message="<p>You have recently registered on E-WALLET</p>",
    )
