from decimal import Decimal

from django.db import transaction
from django_extended.constants import TransactionType
from wallets.models import Wallet


def wallet_transactions(wallet_id: int, receiver_id: int | None, amount: Decimal, transaction_type: str):
    wallet = Wallet.objects.get(id=wallet_id)
    match transaction_type:
        case TransactionType.DEPOSIT:
            wallet.balance += amount
        case TransactionType.WITHDRAW:
            wallet.balance -= amount
        case TransactionType.TRANSFER:
            if receiver_id is None:
                return
            with transaction.atomic():
                receiver_wallet = Wallet.objects.get(id=receiver_id)
                wallet.balance -= amount
                receiver_wallet.balance += amount
                receiver_wallet.save()
    wallet.save()


def cancel_wallet_transactions(wallet_id: int, receiver_id: int, amount: Decimal, transaction_type: str):
    wallet = Wallet.objects.get(id=wallet_id)
    match transaction_type:
        case TransactionType.DEPOSIT:
            wallet.balance -= amount
        case TransactionType.WITHDRAW:
            wallet.balance += amount
        case TransactionType.TRANSFER:
            receiver_wallet = Wallet.objects.get(id=receiver_id)
            wallet.balance += amount
            receiver_wallet.balance -= amount
            receiver_wallet.save()
    wallet.save()
