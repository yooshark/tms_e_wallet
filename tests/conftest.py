import pytest
from django_extended.constants import UserRole
from rest_framework.test import APIClient

from tests.users.factories import UserFactory


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture
def wallet_owner():
    user = UserFactory()
    user.role = UserRole.WALLET_OWNER
    user.save()
    return user


@pytest.fixture
def admin_user():
    user = UserFactory(is_staff=True, is_superuser=True)
    user.role = UserRole.ADMIN
    user.save()
    return user
