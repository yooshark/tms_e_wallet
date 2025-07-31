from decimal import Decimal
from typing import Any

from django.core.validators import MinValueValidator
from django_extended.constants import RequestMethods
from rest_framework import serializers
from wallets.models import Wallet


class WalletsListCreateSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(required=False)
    balance = serializers.DecimalField(
        max_digits=32,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        default=Decimal("0.0"),
    )

    class Meta:
        model = Wallet
        fields = (
            "id",
            "owner_id",
            "name",
            "wallet_number",
            "balance",
        )

    def validate(self, attrs: dict[str, Any]):
        request = self.context.get("request")
        if request and request.method == RequestMethods.POST:
            attrs.pop("wallet_number", None)
            attrs.pop("balance", None)
        return attrs

    def create(self, validated_data: dict[str, Any]):
        user = self.context["request"].user
        if not user.is_admin:
            validated_data["owner_id"] = user.id
            return Wallet.objects.create(**validated_data)
        return Wallet.objects.create(**validated_data)


class WalletsRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=32, decimal_places=2, validators=[MinValueValidator(0.0)])

    class Meta:
        model = Wallet
        fields = (
            "id",
            "name",
            "balance",
        )

    def validate_balance(self, balance: Decimal) -> Decimal:
        user = self.context["request"].user
        if user.is_wallet_owner and balance:
            raise serializers.ValidationError({"balance": "The user cannot change the balance"})
        return balance


class WalletsBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = (
            "id",
            "balance",
        )
