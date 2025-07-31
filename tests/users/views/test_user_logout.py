import pytest


@pytest.mark.django_db
class TestPost:
    def test_logout(self, api_client, wallet_owner):
        api_client.force_authenticate(wallet_owner)
        response = api_client.post("/api/users/logout/")
        assert response.status_code == 200
        assert response.data["success"] == "Successfully logged out"

    def test_it_returns_error_if_auth_credentials_were_not_provided(self, api_client):
        response = api_client.post("/api/users/logout/")
        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."
