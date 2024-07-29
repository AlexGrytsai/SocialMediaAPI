from django.http import HttpResponseRedirect
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
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
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        if (self.request.method == "PUT" and
            self.kwargs.get("action") == "update_password"):
            return UserPasswordUpdateSerializer
        return UserUpdateSerializer

    def update_password(self, request, *args, **kwargs):
        """
        Update the password of a user.
        """
        self.kwargs["action"] = "update_password"
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.set_password(serializer.validated_data["password"])
        user.save()
        return Response({"detail": "Password updated successfully."},
                        status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        if "update-password" in request.path:
            return self.update_password(request, *args, **kwargs)
        return super().put(request, *args, **kwargs)
