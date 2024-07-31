from django.db.models import Exists, OuterRef
from django.http import HttpResponseRedirect, HttpRequest
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

from users.models import User
from users.serializers import UserCreateSerializer, UserListSerializer, \
    UserDetailSerializer, UserUpdateSerializer, UserPasswordUpdateSerializer, \
    UserManageSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().select_related("residence_place")
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserCreateSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return (IsAdminUser(),)
        if self.request.method == "POST":
            return (AllowAny(),)
        return super().get_permissions()

    def get_queryset(self):
        username = self.request.query_params.get("username")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        residence = self.request.query_params.get("residence")
        birth_date = self.request.query_params.get("birthdate")

        queryset = super(UserViewSet, self).get_queryset()

        if username:
            queryset = queryset.filter(username__icontains=username)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        if residence:
            queryset = queryset.filter(residence_place__name=residence)
        if birth_date:
            queryset = queryset.filter(birth_date__icontains=birth_date)

        user = self.request.user
        queryset = queryset.annotate(
            is_following=Exists(
                User.objects.filter(id=user.id, followers=OuterRef("id"))
            ),
            subscribed=Exists(
                User.objects.filter(
                    id=user.id, my_subscriptions=OuterRef("id")
                )
            )
        )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a user by their ID. If the user ID matches the current
        user's ID, redirect to the 'users:me' endpoint.
        Otherwise, call the parent class's retrieve method.
        """
        user_id = kwargs.get("pk")
        if str(user_id) == str(self.request.user.id):
            url = reverse("users:me", request=request)
            return HttpResponseRedirect(
                url,
                status=status.HTTP_308_PERMANENT_REDIRECT
            )
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["GET"],
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request: HttpRequest, pk: int = None):
        user = self.request.user
        user_to_subscribe = get_object_or_404(User, pk=pk)
        if user_to_subscribe in user.my_subscriptions.all():
            return Response(
                data={
                    "message":
                        f"Already followed from {user_to_subscribe} (id={pk})"
                },
                status=status.HTTP_200_OK
            )
        user.my_subscriptions.add(user_to_subscribe)
        user_to_subscribe.followers.add(user)
        return Response(
            data={"message": f"Subscribed from {user_to_subscribe} (id={pk})"},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["GET"],
        url_path="unsubscribe",
        url_name="unsubscribe",
        permission_classes=[IsAuthenticated],
    )
    def unsubscribe(self, request: HttpRequest, pk: int = None):
        user = self.request.user
        user_to_unsubscribe = get_object_or_404(User, pk=pk)
        if user_to_unsubscribe not in user.my_subscriptions.all():
            return Response(
                data={
                    "message":
                        f"Not followed from {user_to_unsubscribe} (id={pk})"
                },
                status=status.HTTP_200_OK
            )
        user.my_subscriptions.remove(user_to_unsubscribe)
        user_to_unsubscribe.followers.remove(user)
        return Response(
            data={
                "message": f"Unsubscribed from {user_to_unsubscribe} (id={pk})"
            },
            status=status.HTTP_200_OK
        )


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited without a password.
    """
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        return User.objects.all().filter(id=user.id).select_related(
            "residence_place"
        )

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserManageSerializer
        return UserUpdateSerializer


class UserPasswordUpdateView(generics.UpdateAPIView):
    """
    API endpoint that allows users update their password.
    """
    serializer_class = UserPasswordUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
