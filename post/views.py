from django.http import HttpRequest, HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from post.models import Post
from post.serializers import PostSerializer, PostListSerializer, \
    PostDetailSerializer, CommentSerializer


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
        if self.action == "add_comment":
            return CommentSerializer
        return super().get_serializer_class()

    @staticmethod
    def _get_params_hashtag(qr_params: str) -> list:
        return [hashtag.lower() for hashtag in qr_params.split(",")]

    def get_queryset(self):
        queryset = super(PostViewSet, self).get_queryset()
        hashtags = self.request.query_params.get("hashtag")
        author = self.request.query_params.get("author")

        if hashtags:
            queryset = queryset.filter(
                hashtags__tag__in=self._get_params_hashtag(hashtags)
            )
        if author:
            queryset = queryset.filter(owner__username=author)

        return queryset

    @action(
        detail=True,
        methods=["POST"],
        url_path="add-comment",
        url_name="add-comment",
        permission_classes=[IsAuthenticated],
    )
    def add_comment(
        self,
        request: HttpRequest,
        pk: int = None
    ) -> HttpResponse:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
