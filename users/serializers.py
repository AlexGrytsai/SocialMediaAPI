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
            "first_name",
            "last_name",
            "birth_date",
            "photo",
            "residence_place",
        ]
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
            "birth_date": {
                "required": False,
                "style": {
                    "input_type": "date",
                    "placeholder": "Birth date (optional)"
                }
            },
            "photo": {
                "required": False
            }
        }


class UserListSerializer(serializers.ModelSerializer):
    """User model list serializer."""
    residence_place = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "residence_place"
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """User model detail serializer."""
    residence_place = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "is_staff",
            "first_name",
            "last_name",
            "birth_date",
            "residence_place",
            "photo",
            "followers",
            "my_subscriptions",
        ]


class UserUpdateAddSerializer(UserCreateSerializer):
    """User model serializer for updating and adding with staff permissions."""

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields.copy()
        fields.remove("password")
