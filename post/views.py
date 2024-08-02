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

    @staticmethod
    def _get_params_hashtag(qr_params: str) -> list:
        return [hashtag.lower() for hashtag in qr_params.split(",")]

    def get_queryset(self):
        hashtags = self.request.query_params.get("hashtag")

        if hashtags:
            return self.queryset.filter(
                hashtags__tag__in=self._get_params_hashtag(hashtags)
            )
        return self.queryset
