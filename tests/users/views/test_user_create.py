from unittest import mock

import pytest
from django.conf import settings
from users.tasks import send_registration_email

from tests.users.factories import UserFactory


@pytest.mark.django_db
class TestPost:
    def test_it_creates_user(self, api_client):
        user = UserFactory.build()

        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "password": user.password,
            "confirm_password": user.password,
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 201
        assert response.data["email"] == user.email

    def test_it_returns_error_if_email_was_not_entered(self, api_client):
        user = UserFactory.build()

        data = {
            "password": user.password,
            "confirm_password": user.password,
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["email"] == ["This field is required."]

    def test_it_returns_error_if_passwords_were_not_entered(self, api_client):
        user = UserFactory.build()

        data = {
            "email": user.email,
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["password"] == ["This field is required."]
        assert response.data["confirm_password"] == ["This field is required."]

    def test_it_returns_error_if_password_was_not_confirmed(self, api_client):
        user = UserFactory.build()

        data = {
            "email": user.email,
            "password": "passw0rd123",
            "confirm_password": "test_password",
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["confirm_password"] == ["The password not confirmed"]

    def test_it_returns_error_if_password_is_too_common(self, api_client):
        user = UserFactory.build()

        data = {
            "email": user.email,
            "password": "passw0rd",
            "confirm_password": "passw0rd",
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["password"][0] == "This password is too common."

    def test_it_returns_error_if_email_already_exists(self, api_client):
        UserFactory(email="test@example.com")
        user = UserFactory.build()

        data = {
            "email": "test@example.com",
            "password": user.password,
            "confirm_password": user.password,
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["email"][0] == "This email already exist"

    @pytest.mark.skipif(not settings.CELERY_RUN, reason="requires running Celery")
    @mock.patch.object(send_registration_email, "delay")
    @pytest.mark.django_db
    def test_it_sends_message_to_email_upon_successful_registration(self, mock_delay, api_client):
        user = UserFactory.build()
        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": "test@example.com",
            "password": user.password,
            "confirm_password": user.password,
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 201
        mock_delay.assert_called_once()

    @pytest.mark.skipif(not settings.CELERY_RUN, reason="requires running Celery")
    @mock.patch.object(send_registration_email, "delay")
    @pytest.mark.django_db
    def test_it_does_not_send_message_if_registration_failed(self, mock_delay, api_client):
        user = UserFactory.build()
        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": user.password,
            "confirm_password": user.password,
        }

        response = api_client.post("/api/users/register/", data=data, format="json")

        assert response.status_code == 400
        mock_delay.assert_not_called()
