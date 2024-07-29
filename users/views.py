from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.serializers import UserSerializer, UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated,]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,]

    def get_object(self):
        return self.request.user
