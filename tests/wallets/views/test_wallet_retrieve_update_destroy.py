from decimal import Decimal

import pytest
from django_extended.constants import TransactionType

from tests.users.factories import UserFactory
from tests.wallets.factories import TransactionFactory, WalletFactory


@pytest.mark.django_db
class TestGet:
    def test_it_returns_wallet(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="ecf104a3-9e47-464f-9156-20688af1339e",
            balance=Decimal("100.0"),
        )

        response = api_client.get(f"/api/wallets/{wallet.pk}/")

        assert response.status_code == 200

    def test_it_returns_error_if_user_is_not_auth(self, api_client, wallet_owner):
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="3309cef5-ca5b-4f91-b8e2-47bd61dda81c",
            balance=Decimal("0.0"),
        )

        response = api_client.get(f"/api/wallets/{wallet.pk}/")

        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_it_returns_wallet_if_user_is_admin(self, api_client, wallet_owner, admin_user):
        api_client.force_authenticate(admin_user)
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="2c198326-2612-4d0a-ac16-886262a0874d",
            balance=Decimal("0.0"),
        )

        response = api_client.get(f"/api/wallets/{wallet.pk}/")

        assert response.status_code == 200


@pytest.mark.django_db
class TestPatch:
    def test_it_updates_wallet(self, api_client, wallet_owner, admin_user):
        api_client.force_authenticate(admin_user)
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="07c63267-752b-4ee8-b0c0-9b7e02f45b6c",
            balance=Decimal("0.0"),
        )
        data = {
            "name": "new_name",
            "balance": Decimal("144.00"),
        }

        response = api_client.patch(f"/api/wallets/{wallet.pk}/", data=data, format="json")

        assert response.status_code == 200
        wallet.refresh_from_db()
        assert data["name"] == wallet.name
        assert data["balance"] == wallet.balance

    def test_it_updates_name_if_auth_user_is_wallet_owner(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="07c63267-752b-4ee8-b0c0-9b7e02f45b6c",
            balance=Decimal("0.0"),
        )
        data = {
            "name": "new_name",
        }

        response = api_client.patch(f"/api/wallets/{wallet.pk}/", data=data, format="json")

        assert response.status_code == 200
        wallet.refresh_from_db()
        assert data["name"] == wallet.name

    def test_it_returns_error_if_user_changes_balance(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="07c63267-752b-4ee8-b0c0-9b7e02f45b6c",
            balance=Decimal("0.0"),
        )
        data = {
            "balance": Decimal("100.0"),
        }

        response = api_client.patch(f"/api/wallets/{wallet.pk}/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["balance"]["balance"] == "The user cannot change the balance"

    def test_it_returns_error_if_user_updates_not_his_wallet(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        user = UserFactory()
        wallet = WalletFactory(
            owner=user,
            name="name",
            wallet_number="07c63267-752b-4ee8-b0c0-9b7e02f45b6c",
            balance=Decimal("0.0"),
        )
        data = {
            "name": "new_name",
        }

        response = api_client.patch(f"/api/wallets/{wallet.pk}/", data=data, format="json")

        assert response.status_code == 404
        assert response.data["detail"] == "Not found."


@pytest.mark.django_db
class TestDelete:
    def test_it_deletes_wallet(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="07c63267-752b-4ee8-b0c0-9b7e02f45b6c",
            balance=Decimal("0.0"),
        )

        response = api_client.delete(f"/api/wallets/{wallet.pk}/")

        assert response.status_code == 204

    def test_it_deletes_wallet_by_admin(self, api_client, wallet_owner, admin_user):
        api_client.force_authenticate(admin_user)
        wallet = WalletFactory(
            owner=wallet_owner,
            name="name",
            wallet_number="07c63267-752b-4ee8-b0c0-9b7e02f45b6c",
            balance=Decimal("0.0"),
        )

        response = api_client.delete(f"/api/wallets/{wallet.pk}/")

        assert response.status_code == 204

    def test_it_deletes_wallet_if_it_has_transactions(self, api_client, wallet_owner):
        user = UserFactory()
        wallet1 = WalletFactory(owner=user, balance=Decimal("0.0"))
        wallet2 = WalletFactory(owner=wallet_owner, balance=Decimal("1000.0"))
        TransactionFactory(
            wallet=wallet2,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("10"),
        )
        TransactionFactory(
            wallet=wallet2,
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("20"),
        )
        TransactionFactory(
            wallet=wallet2,
            receiver=wallet1,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("100.0"),
        )
        api_client.force_authenticate(wallet_owner)

        response = api_client.delete(f"/api/wallets/{wallet2.pk}/")

        assert response.status_code == 204
