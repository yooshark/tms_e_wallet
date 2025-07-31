import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django_extended.constants import MINIMUM_TRANSFER_RATE, TransactionType
from django_extended.models import BaseModel
from users.models import User


class Wallet(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets")
    name = models.CharField(max_length=255)
    wallet_number = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    balance = models.DecimalField(
        max_digits=32,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        default=Decimal("0.0"),
    )

    def clean(self):
        if self.balance < Decimal("0.0") and self.balance != Decimal("0.0"):
            raise ValidationError({"balance": "The balance should be positive"})
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Transaction(BaseModel):
    wallet = models.ForeignKey(
        "Wallet",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    receiver = models.ForeignKey(
        "Wallet",
        on_delete=models.CASCADE,
        related_name="incoming_transactions",
        blank=True,
        null=True,
    )
    amount = models.DecimalField(max_digits=32, decimal_places=2)
    transaction_type = models.CharField(choices=TransactionType.choices)

    def clean(self):
        if self.amount < MINIMUM_TRANSFER_RATE:
            raise ValidationError({"amount": "Insufficient transfer amount, the minimum amount is 0.1"})
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
