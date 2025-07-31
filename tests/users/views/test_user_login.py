import ast

import pytest
from users.models import User


@pytest.mark.django_db
class TestPost:
    def setup_method(self):
        self.password = "testpassw0rd!"
        self.email = "test@example.com"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.endpoint = "/api/users/login/"

    def test_user_login(self, api_client):
        data = {"email": self.email, "password": self.password}
        response = api_client.post(self.endpoint, data=data)
        assert response.status_code == 200
        dict_str = response.content.decode("UTF-8")
        response_data = ast.literal_eval(dict_str)
        expected_data = {"id": self.user.id, "email": self.user.email}
        assert response_data == expected_data

    def test_it_returns_error_if_required_field_was_not_entered(self, client):
        data = {"email": self.email}
        response = client.post(self.endpoint, data=data)

        assert response.status_code == 400
        dict_str = response.content.decode("UTF-8")
        response_data = ast.literal_eval(dict_str)
        expected_data = {"password": ["This field is required."]}
        assert response_data == expected_data

    def test_it_returns_error_if_incorrect_email_was_entered(self, client):
        data = {"email": "no_test@example.com", "password": self.password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 401
        dict_str = response.content.decode("UTF-8")
        response_data = ast.literal_eval(dict_str)
        expected_data = {"detail": "Invalid credentials, try it again"}
        assert response_data == expected_data

    def test_it_returns_error_if_incorrect_password_was_entered(self, client):
        data = {"email": self.email, "password": "testpass"}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 401
        dict_str = response.content.decode("UTF-8")
        response_data = ast.literal_eval(dict_str)
        expected_data = {"detail": "Invalid credentials, try it again"}
        assert response_data == expected_data
