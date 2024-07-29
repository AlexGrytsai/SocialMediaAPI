from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """User model serializer."""
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "is_staff",
            "first_name",
            "last_name"
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
                "style": {"input_type": "text", "placeholder": "Username"},
            },
            "first_name": {
                "required": False,
                "style": {"input_type": "text", "placeholder": "First Name"}
            },
            "last_name": {
                "required": False,
                "style": {"input_type": "text", "placeholder": "Last Name"}
            }
        }
