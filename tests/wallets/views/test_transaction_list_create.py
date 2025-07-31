from decimal import Decimal

import pytest
from django_extended.constants import TransactionType

from tests.users.factories import UserFactory
from tests.wallets.factories import TransactionFactory, WalletFactory


@pytest.mark.django_db
class TestPost:
    def test_it_tops_up_balance(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("0"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("100.00"),
            "transaction_type": TransactionType.DEPOSIT,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 201
        wallet.refresh_from_db()
        assert data["amount"] == wallet.balance

    def test_it_tops_up_balance_of_another_user(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user = UserFactory()
        wallet = WalletFactory(owner=user, balance=Decimal("1.0"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("99.00"),
            "transaction_type": TransactionType.DEPOSIT,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 201
        wallet.refresh_from_db()
        assert wallet.balance == Decimal("100.0")

    def test_it_withdraws_amount_from_another_user_if_auth_user_is_admin(self, api_client, admin_user):
        api_client.force_authenticate(admin_user)
        user = UserFactory()
        wallet = WalletFactory(owner=user, balance=Decimal("100.0"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("100.00"),
            "transaction_type": TransactionType.WITHDRAW,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 201

    def test_it_withdraws_from_wallet_balance(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("99.00"),
            "transaction_type": TransactionType.WITHDRAW,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 201
        wallet.refresh_from_db()
        assert wallet.balance == Decimal("1.00")

    def test_it_returns_error_if_amount_is_more_than_balance(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("10.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("90.00"),
            "transaction_type": TransactionType.WITHDRAW,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["amount"] == ["There are not enough funds on the balance, enter a smaller amount"]

    def test_it_returns_error_if_user_is_not_auth(self, api_client, wallet_owner):
        wallet = WalletFactory(owner=wallet_owner)
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("99.00"),
            "transaction_type": TransactionType.DEPOSIT,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_it_returns_error_if_amount_is_less_than_minimum_transfer_rate(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner)
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("0.0"),
            "transaction_type": TransactionType.WITHDRAW,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["amount"]["amount"] == "Insufficient transfer amount, the minimum amount is 0.1"

    def test_it_does_not_withdraw_if_user_is_not_owner(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user = UserFactory()
        wallet = WalletFactory(owner=user, balance=Decimal("100.0"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("100.00"),
            "transaction_type": TransactionType.WITHDRAW,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["wallet_id"] == ["The user must be the owner of the wallet."]

    def test_it_sends_amount(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user = UserFactory()
        wallet1 = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        wallet2 = WalletFactory(owner=user, balance=Decimal("100.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet1.pk,
            "receiver_id": wallet2.pk,
            "amount": Decimal("50.00"),
            "transaction_type": TransactionType.TRANSFER,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 201
        wallet1.refresh_from_db()
        wallet2.refresh_from_db()
        assert wallet1.balance == Decimal("50")
        assert wallet2.balance == Decimal("150")

    def test_it_returns_error_if_sender_balance_is_less_than_amount(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user = UserFactory()
        wallet1 = WalletFactory(owner=wallet_owner, balance=Decimal("1.00"))
        wallet2 = WalletFactory(owner=user, balance=Decimal("100.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet1.pk,
            "receiver_id": wallet2.pk,
            "amount": Decimal("50.00"),
            "transaction_type": TransactionType.TRANSFER,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["amount"] == ["There are not enough funds on the balance, enter a smaller amount"]

    def test_it_returns_error_if_wallets_do_not_exist(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        TransactionFactory.build()
        data = {
            "wallet_id": 123,
            "receiver_id": 321,
            "amount": Decimal("5.00"),
            "transaction_type": TransactionType.TRANSFER,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["wallet_id"]["wallet_id"] == "The wallet does not exist."
        assert response.data["receiver_id"]["receiver_id"] == "The wallet does not exist."

    def test_it_returns_error_if_receiver_wallet_was_not_entered(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "amount": Decimal("5.00"),
            "transaction_type": TransactionType.TRANSFER,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["receiver_id"] == ["The wallet of the recipient must be entered."]

    def test_it_returns_error_if_user_is_not_owner_of_sender_wallet(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user1 = UserFactory()
        user2 = UserFactory()
        wallet1 = WalletFactory(owner=user1, balance=Decimal("100.00"))
        wallet2 = WalletFactory(owner=user2, balance=Decimal("10.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet1.pk,
            "receiver_id": wallet2.pk,
            "amount": Decimal("5.00"),
            "transaction_type": TransactionType.TRANSFER,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["wallet_id"] == ["The user must be the owner of the wallet."]

    def test_it_sends_amount_if_auth_user_is_admin(self, api_client, wallet_owner, admin_user):
        api_client.force_authenticate(admin_user)
        user = UserFactory()
        wallet1 = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        wallet2 = WalletFactory(owner=user, balance=Decimal("10.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet1.pk,
            "receiver_id": wallet2.pk,
            "amount": Decimal("50.00"),
            "transaction_type": TransactionType.TRANSFER,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 201
        wallet1.refresh_from_db()
        wallet2.refresh_from_db()
        assert wallet1.balance == Decimal("50")
        assert wallet2.balance == Decimal("60")

    def test_it_returns_error_if_transaction_is_transfer_and_recipient_was_specified(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet1 = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        wallet2 = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet1.pk,
            "receiver_id": wallet2.pk,
            "amount": Decimal("5.00"),
            "transaction_type": TransactionType.DEPOSIT,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["receiver_id"] == [
            "The recipient can only be specified if the transaction type is transfer"
        ]

    def test_it_does_not_allow_to_transfer_from_the_same_wallet(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("100"))
        TransactionFactory.build()
        data = {
            "wallet_id": wallet.pk,
            "receiver_id": wallet.pk,
            "amount": Decimal("90.00"),
            "transaction_type": TransactionType.TRANSFER,
        }

        response = api_client.post("/api/wallets/transactions/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["receiver_id"] == ["The recipient cannot be the sender"]


@pytest.mark.django_db
class TestGet:
    def test_it_returns_transaction(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user = UserFactory()
        wallet1 = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        wallet2 = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        wallet3 = WalletFactory(owner=user, balance=Decimal("0.00"))
        TransactionFactory(
            wallet=wallet1,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("2.0"),
        )
        TransactionFactory(
            wallet=wallet1,
            transaction_type=TransactionType.WITHDRAW,
            amount=Decimal("2.0"),
        )
        TransactionFactory(
            wallet=wallet2,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("2.0"),
        )
        TransactionFactory(
            wallet=wallet2,
            receiver=wallet3,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("100.0"),
        )
        response = api_client.get("/api/wallets/transactions/")

        assert response.status_code == 200
        assert len(response.data) == 4

    def test_it_users_transactions_if_auth_user_is_admin(self, api_client, wallet_owner, admin_user):
        api_client.force_authenticate(admin_user)
        user = UserFactory()
        wallet1 = WalletFactory(owner=user, balance=Decimal("100.00"))
        wallet2 = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))

        TransactionFactory(
            wallet=wallet1,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("20.0"),
        )
        TransactionFactory(
            wallet=wallet1,
            transaction_type=TransactionType.WITHDRAW,
            amount=Decimal("2.0"),
        )
        TransactionFactory(
            wallet=wallet2,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("2.0"),
        )
        TransactionFactory(
            wallet=wallet2,
            transaction_type=TransactionType.WITHDRAW,
            amount=Decimal("20.0"),
        )

        response = api_client.get("/api/wallets/transactions/")

        assert response.status_code == 200
        assert len(response.data) == 4

    def test_it_returns_error_if_user_is_not_auth(self, api_client, wallet_owner):
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        TransactionFactory(
            wallet=wallet,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("2.0"),
        )

        response = api_client.get("/api/wallets/transactions/")

        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_it_returns_transaction_if_user_is_sender_and_recipient(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user1 = UserFactory()
        user2 = UserFactory()
        wallet1 = WalletFactory(owner=wallet_owner, balance=Decimal("0.00"))
        wallet2 = WalletFactory(owner=user1, balance=Decimal("0.00"))
        wallet3 = WalletFactory(owner=user2, balance=Decimal("0.00"))
        TransactionFactory(
            wallet=wallet1,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("1000.0"),
        )
        TransactionFactory(
            wallet=wallet1,
            receiver=wallet2,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("100.0"),
        )
        TransactionFactory(
            wallet=wallet1,
            receiver=wallet3,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("100.0"),
        )
        TransactionFactory(
            wallet=wallet2,
            receiver=wallet1,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("10.0"),
        )
        TransactionFactory(
            wallet=wallet3,
            receiver=wallet1,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("10.0"),
        )
        TransactionFactory(
            wallet=wallet2,
            receiver=wallet3,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("10.0"),
        )
        TransactionFactory(
            wallet=wallet3,
            receiver=wallet2,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("20.0"),
        )

        response = api_client.get("/api/wallets/transactions/")

        assert response.status_code == 200

    def test_it_shows_wallet_balance_before_transfer(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user = UserFactory()
        wallet1 = WalletFactory(owner=wallet_owner, balance=Decimal("99.00"))
        wallet2 = WalletFactory(owner=user)
        TransactionFactory(
            wallet=wallet1,
            receiver=wallet2,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("70.0"),
        )

        response = api_client.get("/api/wallets/transactions/")

        assert response.status_code == 200
        assert Decimal(response.data[0]["wallet_balance"]) == Decimal("99.00")

    def test_it_shows_wallet_balance_before_deposit(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("0.00"))
        TransactionFactory(
            wallet=wallet,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("77.0"),
        )

        response = api_client.get("/api/wallets/transactions/")

        assert response.status_code == 200
        assert Decimal(response.data[0]["wallet_balance"]) == Decimal("0")

    def test_it_shows_wallet_balance_before_withdraw(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(owner=wallet_owner, balance=Decimal("100.00"))
        TransactionFactory(
            wallet=wallet,
            transaction_type=TransactionType.WITHDRAW,
            amount=Decimal("77.0"),
        )

        response = api_client.get("/api/wallets/transactions/")

        assert response.status_code == 200
        assert Decimal(response.data[0]["wallet_balance"]) == Decimal("100")
