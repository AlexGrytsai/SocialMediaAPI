from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
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

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                _("A user with that username already exists.")
            )
        return value

    def validate_birth_date(self, value: str) -> str:
        try:
            birth_date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise serializers.ValidationError(
                _("Birth date must be in the format YYYY-MM-DD.")
            )
        age = (date.today() - birth_date).days // 365
        if age < 13:
            raise serializers.ValidationError(
                _("User must be at least 13 years old.")
            )
        if age > 100:
            raise serializers.ValidationError(
                _("User must be less than 100 years old.")
            )
        return value

    def create(self, validated_data: dict) -> User:
        return get_user_model().objects.create_user(**validated_data)


class UserListSerializer(serializers.ModelSerializer):
    """User model list serializer."""
    residence_place = serializers.StringRelatedField()
    is_following = serializers.BooleanField()
    subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "residence_place",
            "is_following",
            "subscribed"
        ]


class UserDetailFollowersAndSubscriptionsSerializer(
    serializers.ModelSerializer
):
    """
    Serializer for the User model to display followers and subscriptions.

    This serializer is used to display the followers and subscriptions of
    a user. It includes the user's id, username, and full name.
    """
    name = serializers.CharField(source="full_name")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
        ]


class UserManageSerializer(serializers.ModelSerializer):
    """User model serializer for managing a user profile."""
    residence_place = serializers.StringRelatedField()
    followers = UserDetailFollowersAndSubscriptionsSerializer(many=True)
    subscriptions = serializers.SerializerMethodField()

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
            "subscriptions",
        ]

    def get_subscriptions(self, obj):
        return UserDetailFollowersAndSubscriptionsSerializer(
            obj.my_subscriptions, many=True
        ).data


class UserDetailSerializer(UserManageSerializer):
    """
    Serializer for the User model to display detailed information about a user.

    This serializer extends the UserManageSerializer and adds additional fields
    to display whether the user is following another user and whether the user
    is subscribed to another user.
    """
    is_following = serializers.BooleanField()
    subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = UserManageSerializer.Meta.fields + [
            "is_following",
            "subscribed",
        ]


class UserUpdateSerializer(UserCreateSerializer):
    """User model serializer for updating a user profile without a password."""

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields.copy()
        fields.remove("password")

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                _("A user with that username already exists.")
            )
        return value

    def validate_birth_date(self, value: str) -> str:
        try:
            birth_date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise serializers.ValidationError(
                _("Birth date must be in the format YYYY-MM-DD.")
            )
        age = (date.today() - birth_date).days // 365
        if age < 13:
            raise serializers.ValidationError(
                _("User must be at least 13 years old.")
            )
        if age > 100:
            raise serializers.ValidationError(
                _("User must be less than 100 years old.")
            )
        return value


class UserPasswordUpdateSerializer(serializers.ModelSerializer):
    """User model serializer for updating a user's password."""

    class Meta:
        model = User
        fields = ["password"]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "max_length": 128,
                "validators": [validate_password],
                "style": {"input_type": "password", "placeholder": "Password"},
            },
        }

    def update(self, instance: User, validated_data: dict) -> User:
        instance.set_password(validated_data["password"])
        instance.save()
        return instance
