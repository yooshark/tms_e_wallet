from django.contrib.auth.models import BaseUserManager
from django_extended.constants import UserRole
from django.db import models


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email: str, password: str | None = None, **extra_fields) -> models.Model:
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields) -> models.Model:
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
