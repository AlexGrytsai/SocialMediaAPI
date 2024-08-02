from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from post.models import Post
from post.serializers import PostSerializer, PostListSerializer, \
    PostDetailSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("owner").prefetch_related(
        "hashtags"
    )
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return super().get_serializer_class()
