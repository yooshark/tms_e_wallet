from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from tests.wallets.factories import WalletFactory


@pytest.mark.django_db(transaction=True)
class TestConstraints:
    def test_it_should_raise_exception_if_balance_is_not_positive(self, wallet_owner):
        with pytest.raises(ValidationError):
            WalletFactory(
                owner=wallet_owner,
                name="wallet_name",
                wallet_number="test_number",
                balance=Decimal("-123.12"),
            )
