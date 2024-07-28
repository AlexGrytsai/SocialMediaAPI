from __future__ import annotations

import os.path
import uuid

import pycountry
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str,
        **extra_fields
    ) -> "User":
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: str = None,
        **extra_fields
    ) -> "User":
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields
    ) -> "User":
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class ResidencePlace(models.Model):
    country = models.CharField(
        max_length=100,
        db_comment="Name of the user's country of residence. Not required.",
        help_text="Name of the user's country of residence. Not required.",
        null=True,
        blank=True,
    )
    code_country = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        db_comment="Country and territory codes (ISO 3166-1).",
    )

    def clean(self):
        if pycountry.countries.get(name=self.country) is None:
            raise ValueError("Country not found")
        if pycountry.countries.get(name=self.country):
            code_country = pycountry.countries.get(
                name=self.country
            )["alpha_2"]
            self.code_country = code_country

    def delete(self, *args, **kwargs):
        if self.user_set.count() > 0:
            raise ValueError("Cannot delete a country with users")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.country} ({self.code_country})"

    class Meta:
        ordering = ["country"]
        indexes = [
            models.Index(fields=["country", "code_country"]),
        ]


def create_custom_path_for_photo(instance: User, filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return f"users-photos/{instance.email}/{uuid.uuid4()}{extension}"


class User(AbstractUser):
    """
    Custom User model that uses email as the username.
    """

    # Remove the username field and use email as the username.
    username = models.CharField(
        _("username"), max_length=150, blank=True, null=True
    )

    # Add an email field with a unique constraint.
    email = models.EmailField(_("email address"), unique=True)

    # Set the USERNAME_FIELD to email.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Use the custom UserManager.
    objects = UserManager()

    photo = models.ImageField(
        upload_to=create_custom_path_for_photo,
        null=True,
        blank=True,
        db_comment="Photo of the user.",
        help_text="Photo of the user.",
    )

    residence_place = models.ForeignKey(
        ResidencePlace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_comment="Residence place of the user.",
        help_text="Residence place of the user.",
    )

    def clean(self):
        if self.photo:
            max_image_size = 2097152
            if self.photo.size > max_image_size:
                raise ValueError(
                    f"Photo size should be less than "
                    f"{max_image_size / 1024 / 1024}MB"
                )

    class Meta:
        ordering = ["email", "username"]
        indexes = [
            models.Index(fields=["username", "first_name", "last_name"]),
        ]

    def __str__(self):
        """String representation of the User model."""
        if self.username:
            return self.username
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
