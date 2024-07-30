from django.http import HttpResponseRedirect
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.reverse import reverse

from users.models import User
from users.serializers import UserCreateSerializer, UserListSerializer, \
    UserDetailSerializer, UserUpdateSerializer, UserPasswordUpdateSerializer


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


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited without a password.
    """
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        return User.objects.all().filter(id=user.id).select_related(
            "residence_place"
        ).prefetch_related("followers", "my_subscriptions")

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        return UserUpdateSerializer


class UserPasswordUpdateView(generics.UpdateAPIView):
    """
    API endpoint that allows users update their password.
    """
    serializer_class = UserPasswordUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
