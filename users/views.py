from rest_framework import viewsets

from users.models import User
from users.serializers import UserSerializer, UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer
