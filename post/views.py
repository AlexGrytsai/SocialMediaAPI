from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    extend_schema_view,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from post.models import Post
from post.permissions import IsOwnerOrReadOnly
from post.serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List posts",
        description="Retrieve a list of posts with optional filtering by "
                    "hashtags or author.",
        tags=["Posts"],
        responses={200: PostListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="hashtag",
                description="Filter by hashtags",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="author",
                description="Filter by author username",
                required=False,
                type=str,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a post",
        description="Retrieve details of a specific post by ID.",
        tags=["Posts"],
        responses={200: PostDetailSerializer},
    ),
    create=extend_schema(
        summary="Create a post",
        description="Create a new post.",
        tags=["Posts"],
        responses={201: PostSerializer},
    ),
    update=extend_schema(
        summary="Update a post",
        description="Update details of an existing post.",
        tags=["Posts"],
        responses={200: PostSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update a post",
        description="Partially update details of an existing post.",
        tags=["Posts"],
        responses={200: PostSerializer},
    ),
    destroy=extend_schema(
        summary="Delete a post",
        description="Delete a post by ID.",
        tags=["Posts"],
        responses={204: OpenApiResponse(description="No Content")},
    ),
    add_comment=extend_schema(
        summary="Add a comment to a post",
        description="Add a comment to a specific post by ID.",
        tags=["Posts"],
        responses={201: CommentSerializer},
    ),
    edit_comment=extend_schema(
        summary="Edit a comment on a post",
        description="Edit a specific comment on a post by comment ID.",
        tags=["Posts"],
        responses={200: CommentSerializer},
    ),
    like=extend_schema(
        summary="Like a post",
        description="Like a specific post by ID.",
        tags=["Posts"],
        responses={200: OpenApiResponse(description="Liked the post")},
    ),
    unlike=extend_schema(
        summary="Unlike a post",
        description="Unlike a specific post by ID.",
        tags=["Posts"],
        responses={200: OpenApiResponse(description="Unliked the post")},
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.all().select_related("owner").prefetch_related("hashtags")
    )
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action in ("add_comment", "edit_comment", "like", "unlike"):
            return (IsAuthenticated(),)
        if self.request.method == "GET":
            return (AllowAny(),)
        if self.action in ("update", "partial_update", "destroy"):
            return (IsOwnerOrReadOnly(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action in ("add_comment", "edit_comment"):
            return CommentSerializer
        return super().get_serializer_class()

    @staticmethod
    def _get_params_hashtag(qr_params: str) -> list:
        return [hashtag.lower() for hashtag in qr_params.split(",")]

    def get_queryset(self):
        queryset = super(PostViewSet, self).get_queryset()
        hashtags = self.request.query_params.get("hashtag")
        author = self.request.query_params.get("author")
        title = self.request.query_params.get("title")

        if hashtags:
            queryset = queryset.filter(
                hashtags__tag__in=self._get_params_hashtag(hashtags)
            )
        if author:
            queryset = queryset.filter(owner__username=author)

        if self.action == "list":
            queryset = queryset.annotate(
                comments_count=Count("comments"), likes_count=Count("likes")
            )

        if title:
            queryset = queryset.filter(title__icontains=title)

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "comments__owner", "likes"
            ).annotate(
                comments_count=Count("comments"), likes_count=Count("likes")
            )

        return queryset

    @action(
        detail=True,
        methods=["POST"],
        url_path="add-comment/",
        url_name="add-comment",
        permission_classes=[IsAuthenticated],
    )
    def add_comment(
        self, request: HttpRequest, pk: int = None
    ) -> HttpResponse:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["GET", "PUT", "DELETE"],
        url_path="edit-comment/(?P<comment_id>[^/.]+)",
        url_name="edit-comment",
        permission_classes=[IsAuthenticated],
    )
    def edit_comment(
        self, request: HttpRequest, pk: int = None, comment_id: int = None
    ) -> HttpResponse:
        current_user = self.request.user
        comment = self.get_object().comments.get(id=comment_id)
        if current_user != comment.owner:
            return Response(
                data={
                    "message": "You don't have permission to edit this comment"
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(
            comment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        url_path="like",
        url_name="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request: HttpRequest, pk: int = None) -> HttpResponse:
        user = self.request.user
        post = self.get_object()
        if user in post.likes.all():
            return Response(
                data={"message": "You already liked this post"},
                status=status.HTTP_200_OK,
            )
        post.likes.add(user)
        return Response(
            data={
                "message": f"You liked this post '{post.title}' (id={post.id})"
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["GET"],
        url_path="unlike",
        url_name="unlike",
        permission_classes=[IsAuthenticated],
    )
    def unlike(self, request: HttpRequest, pk: int = None) -> HttpResponse:
        user = self.request.user
        post = self.get_object()
        if user not in post.likes.all():
            return Response(
                data={"message": "You didn't like this post"},
                status=status.HTTP_200_OK,
            )
        post.likes.remove(user)
        return Response(
            data={
                "message": f"You unliked this post '{post.title}' "
                           f"(id={post.id})"
            },
            status=status.HTTP_200_OK,
        )
