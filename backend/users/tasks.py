from app.celery import app
from django_extended.services import send_email_after_registration


@app.task
def send_registration_email(user_email: str) -> None:
    send_email_after_registration(user_email)
