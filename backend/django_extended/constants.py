from decimal import Decimal

from django.db import models

MINIMUM_TRANSFER_RATE = Decimal("0.1")


class UserRole(models.TextChoices):
    ADMIN: str = "ADMIN"
    WALLET_OWNER: str = "WALLET_OWNER"


class TransactionType(models.TextChoices):
    WITHDRAW: str = "WITHDRAW"
    DEPOSIT: str = "DEPOSIT"
    TRANSFER: str = "TRANSFER"
    CANCELLATION: str = "CANCELLATION"


class RequestMethods(models.TextChoices):
    POST: str = "POST"
    PATCH: str = "PATCH"
