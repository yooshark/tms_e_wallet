from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django_extended.constants import TransactionType

from tests.wallets.factories import TransactionFactory, WalletFactory


@pytest.mark.django_db()
class TestConstraints:
    def test_it_should_raise_error_if_amount_is_less_than_minimum_rate(self, wallet_owner):
        wallet = WalletFactory(
            owner=wallet_owner,
            name="wallet_name",
            balance=Decimal("100.0"),
        )

        with pytest.raises(ValidationError):
            TransactionFactory(
                wallet=wallet,
                receiver=None,
                amount=Decimal("0.0"),
                transaction_type=TransactionType.DEPOSIT,
            )
