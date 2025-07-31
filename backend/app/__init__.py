from django.conf import settings

if settings.CELERY_RUN:  # to avoid ModuleNotFoundError: No module named 'wallets.apps'
    from .celery import app as celery_app

    __all__ = ("celery_app",)
