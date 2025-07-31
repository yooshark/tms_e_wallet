import pytest

from tests.users.factories import UserFactory
from tests.wallets.factories import WalletFactory


@pytest.mark.django_db
class TestPost:
    def test_it_creates_wallet_by_active_user(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        wallet = WalletFactory.build()
        data = {
            "name": wallet.name,
        }

        response = api_client.post("/api/wallets/", data=data, format="json")

        assert response.status_code == 201

    def test_it_creates_wallet_by_admin_user(self, api_client, admin_user):
        api_client.force_authenticate(admin_user)
        user = UserFactory()
        wallet = WalletFactory.build()
        data = {
            "owner_id": user.id,
            "name": wallet.name,
        }

        response = api_client.post("/api/wallets/", data=data, format="json")

        assert response.status_code == 201

    def test_it_returns_error_if_user_is_not_active(self, api_client):
        wallet = WalletFactory.build()
        data = {
            "name": wallet.name,
        }

        response = api_client.post("/api/wallets/", data=data, format="json")

        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_it_returns_error_if_required_fields_were_not_entered(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        WalletFactory.build()
        data = {}

        response = api_client.post("/api/wallets/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["name"][0] == "This field is required."


@pytest.mark.django_db
class TestGet:
    def test_it_returns_wallets_list_if_user_is_admin(self, api_client, wallet_owner, admin_user):
        api_client.force_authenticate(admin_user)
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=admin_user)
        WalletFactory(owner=admin_user)

        response = api_client.get("/api/wallets/")

        assert response.status_code == 200
        assert len(response.data) == 4

    def test_it_returns_empty_wallets_list_if_user_is_not_owner(self, api_client, admin_user, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        WalletFactory(owner=admin_user)
        WalletFactory(owner=admin_user)

        response = api_client.get("/api/wallets/")

        assert response.status_code == 200
        assert len(response.data) == 0

    def test_it_returns_wallets_list_of_owner(self, api_client, admin_user, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=admin_user)
        WalletFactory(owner=admin_user)

        response = api_client.get("/api/wallets/")

        assert response.status_code == 200
        assert len(response.data) == 3

    def test_it_returns_error_if_user_is_not_auth(self, api_client, wallet_owner, admin_user):
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=wallet_owner)
        WalletFactory(owner=admin_user)
        WalletFactory(owner=admin_user)

        response = api_client.get("/api/wallets/")

        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."
