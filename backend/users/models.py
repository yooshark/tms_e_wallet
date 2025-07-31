from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django_extended.constants import UserRole
from django_extended.models import BaseModel
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=25, choices=UserRole.choices, default=UserRole.WALLET_OWNER)

    USERNAME_FIELD = "email"

    objects = UserManager()

    class Meta:
        db_table = "users"

    def get_wallets_ids(self) -> list[int]:
        return self.wallets.values_list("id", flat=True)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_wallet_owner(self) -> bool:
        return self.role == UserRole.WALLET_OWNER

    def __str__(self) -> models.EmailField:
        return self.email
