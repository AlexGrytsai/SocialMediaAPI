from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User, ResidencePlace


class UserCreateSerializer(serializers.ModelSerializer):
    """User model serializer."""

    residence_place = serializers.PrimaryKeyRelatedField(
        queryset=ResidencePlace.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "username",
            "is_staff",
            "first_name",
            "last_name",
            "photo",
            "residence_place",
        ]
        read_only_fields = ["is_staff"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "max_length": 128,
                "validators": [validate_password],
                "style": {"input_type": "password", "placeholder": "Password"},
            },
            "username": {
                "required": False,
                "style": {
                    "input_type": "text", "placeholder": "Username (optional)"
                },
            },
            "first_name": {
                "required": False,
                "style": {
                    "input_type": "text",
                    "placeholder": "First Name (optional)"
                }
            },
            "last_name": {
                "required": False,
                "style": {
                    "input_type": "text", "placeholder": "Last Name (optional)"
                }
            },
            "photo": {
                "required": False
            }
        }


class UserListSerializer(serializers.ModelSerializer):
    """User model list serializer."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "residence_place"
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """User model detail serializer."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "residence_place",
            "photo",
            "followers",
            "my_subscriptions",
        ]
