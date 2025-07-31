from decimal import Decimal
from typing import Any

from django_extended.constants import (
    MINIMUM_TRANSFER_RATE,
    RequestMethods,
    TransactionType,
)
from rest_framework import serializers
from users.models import User
from wallets.models import Transaction, Wallet
from wallets.services import cancel_wallet_transactions, wallet_transactions


class TransactionBaseSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.DecimalField(source="wallet.balance", max_digits=32, decimal_places=2, read_only=True)

    def validate_amount(self, amount: Decimal) -> Decimal:
        if amount < MINIMUM_TRANSFER_RATE:
            raise serializers.ValidationError({"amount": "Insufficient transfer amount, the minimum amount is 0.1"})
        return amount

    def validate_wallet_id(self, wallet_id: int) -> int:
        wallet_exists = Wallet.objects.filter(id=wallet_id).exists()
        if not wallet_exists:
            raise serializers.ValidationError({"wallet_id": "The wallet does not exist."})
        return wallet_id

    def validate_receiver_id(self, receiver_id: int) -> int | None:
        if receiver_id is None:
            return
        wallet_exists = Wallet.objects.filter(id=receiver_id).exists()
        if not wallet_exists:
            raise serializers.ValidationError({"receiver_id": "The wallet does not exist."})
        return receiver_id

    def validation_wallet_balance(
        self,
        wallet_id: int | None,
        amount: Decimal | None,
        transaction_type: str,
        request_method: str,
    ) -> None:
        if amount is None:
            return
        if request_method == RequestMethods.PATCH and wallet_id is None:
            return
        wallet = Wallet.objects.get(id=wallet_id)
        if (
            transaction_type == TransactionType.TRANSFER or transaction_type == TransactionType.WITHDRAW
        ) and amount > wallet.balance:
            raise serializers.ValidationError(
                {"amount": "There are not enough funds on the balance, enter a smaller amount"}
            )

    @staticmethod
    def validate_wallet_transaction(
        user: User,
        wallet_id: int | None,
        receiver_id: int,
        transaction_type: str,
        request_method: str,
    ):
        if not transaction_type:
            return
        if (
            (transaction_type == TransactionType.WITHDRAW or transaction_type == TransactionType.TRANSFER)
            and not user.is_admin
            and wallet_id not in user.get_wallets_ids()
        ):
            raise serializers.ValidationError({"wallet_id": "The user must be the owner of the wallet."})
        if transaction_type == TransactionType.TRANSFER and not receiver_id:
            raise serializers.ValidationError({"receiver_id": "The wallet of the recipient must be entered."})
        if receiver_id and transaction_type != TransactionType.TRANSFER:
            raise serializers.ValidationError(
                {"receiver_id": "The recipient can only be specified if the transaction type is transfer"}
            )
        if request_method == RequestMethods.PATCH and transaction_type != TransactionType.CANCELLATION:
            raise serializers.ValidationError(
                {
                    "transaction_type": "The user cannot change transaction types. "
                    "The transaction can only be canceled by the administrator."
                }
            )
        if receiver_id and wallet_id == receiver_id:
            raise serializers.ValidationError({"receiver_id": "The recipient cannot be the sender"})

    def validate(self, attrs: dict[str, Any]):
        user = self.context["request"].user
        request_method = self.context["request"].method
        wallet_id = attrs.get("wallet_id", None)
        receiver_id = attrs["receiver_id"]
        amount = attrs.get("amount")
        transaction_type = attrs.get("transaction_type", "")
        self.validation_wallet_balance(wallet_id, amount, transaction_type, request_method)
        self.validate_wallet_transaction(user, wallet_id, receiver_id, transaction_type, request_method)
        return attrs


class TransactionListCreateSerializer(TransactionBaseSerializer):
    wallet_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField(required=False)
    amount = serializers.DecimalField(
        max_digits=32,
        decimal_places=2,
    )
    transaction_type = serializers.ChoiceField(choices=TransactionType.choices, required=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "wallet_id",
            "receiver_id",
            "amount",
            "transaction_type",
            "wallet_balance",
        )

    def create(self, validated_data: dict[str, Any]):
        wallet_id = validated_data["wallet_id"]
        receiver_id = validated_data.get("receiver_id")
        amount = validated_data["amount"]
        transaction_type = validated_data["transaction_type"]
        wallet_transactions(wallet_id, receiver_id, amount, transaction_type)
        return super().create(validated_data)


class TransactionRetrieveUpdateSerializer(TransactionBaseSerializer):
    wallet_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField(required=False)
    amount = serializers.DecimalField(max_digits=32, decimal_places=2)
    transaction_type = serializers.ChoiceField(choices=TransactionType.choices, required=False)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "wallet_id",
            "receiver_id",
            "amount",
            "transaction_type",
            "wallet_balance",
        )

    def update(self, instance, validated_data: dict[str, Any]):
        wallet_id = instance.wallet.id
        receiver_id = None
        if instance.receiver:
            receiver_id = instance.receiver.id
        amount = validated_data.get("amount", instance.amount)
        transaction_type = instance.transaction_type
        cancellation_type = validated_data.get("transaction_type")
        wallet_transactions(wallet_id, receiver_id, amount, transaction_type)
        if cancellation_type and receiver_id is not None:
            cancel_wallet_transactions(wallet_id, receiver_id, amount, transaction_type)
            instance.transaction_type = cancellation_type
        instance.amount = amount
        instance.save()
        return super().update(instance, validated_data)
