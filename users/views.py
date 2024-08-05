from typing import Type

from django.db.models import Exists, OuterRef, QuerySet, Count
from django.http import HttpResponseRedirect, HttpRequest
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    extend_schema_view,
)
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer

from post.models import Post
from post.serializers import PostListSerializer
from users.models import User
from users.serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserPasswordUpdateSerializer,
    UserManageSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List users",
        description="Retrieve a list of users with optional filtering.",
        tags=["Users"],
        responses={
            200: UserListSerializer,
        },
        parameters=[
            OpenApiParameter(
                name="username",
                description="Filter by username",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="first_name",
                description="Filter by first name",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter by last name",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="residence",
                description="Filter by residence place name",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="birthdate",
                description="Filter by birth date",
                required=False,
                type=str,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a user",
        description="Retrieve details of a specific user by ID.",
        tags=["Users"],
        responses={
            200: UserDetailSerializer,
        },
    ),
    create=extend_schema(
        summary="Create a user",
        description="Create a new user.",
        tags=["Users"],
        responses={
            201: UserCreateSerializer,
        },
    ),
    update=extend_schema(
        summary="Update a user",
        description="Update details of an existing user.",
        tags=["Users"],
        responses={
            200: UserUpdateSerializer,
        },
    ),
    partial_update=extend_schema(
        summary="Partial update a user",
        description="Partially update details of an existing user.",
        tags=["Users"],
        responses={
            200: UserUpdateSerializer,
        },
    ),
    destroy=extend_schema(
        summary="Delete a user",
        description="Delete a user by ID.",
        tags=["Users"],
        responses={
            204: OpenApiResponse(description="No Content"),
        },
    ),
    subscribe=extend_schema(
        summary="Subscribe to a user",
        description="Subscribe to a user by ID.",
        tags=["Users"],
        responses={
            200: OpenApiResponse(description="Subscribed"),
        },
    ),
    unsubscribe=extend_schema(
        summary="Unsubscribe from a user",
        description="Unsubscribe from a user by ID.",
        tags=["Users"],
        responses={
            200: OpenApiResponse(description="Unsubscribed"),
        },
    ),
    my_posts=extend_schema(
        summary="List my posts",
        description="Retrieve a list of posts created by the current user.",
        tags=["Users"],
        responses={
            200: PostListSerializer,
        },
    ),
    my_subscriptions_posts=extend_schema(
        summary="List posts from subscriptions",
        description="Retrieve a list of posts from users the current user is "
                    "subscribed to.",
        tags=["Users"],
        responses={
            200: PostListSerializer,
        },
    ),
    liked_posts=extend_schema(
        summary="List liked posts",
        description="Retrieve a list of posts liked by the current user.",
        tags=["Users"],
        responses={
            200: PostListSerializer,
        },
    ),
)
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
        if self.action in ("my_posts", "my_subscriptions_posts"):
            return PostListSerializer
        return UserCreateSerializer

    def get_permissions(self) -> tuple:
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return (IsAdminUser(),)
        if self.request.method == "POST":
            return (AllowAny(),)
        return super().get_permissions()

    def get_queryset(self) -> QuerySet:
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
            ),
        )

        return queryset

    def retrieve(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """
        Retrieve a user by their ID. If the user ID matches the current
        user's ID, redirect to the 'users:me' endpoint.
        Otherwise, call the parent class's retrieve method.
        """
        user_id = kwargs.get("pk")
        if str(user_id) == str(self.request.user.id):
            url = reverse("users:me", request=request)
            return HttpResponseRedirect(
                url, status=status.HTTP_308_PERMANENT_REDIRECT
            )
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["GET"],
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request: HttpRequest, pk: int = None) -> Response:
        user = self.request.user
        user_to_subscribe = get_object_or_404(User, pk=pk)
        if user_to_subscribe in user.my_subscriptions.all():
            return Response(
                data={
                    "message": f"Already followed from {user_to_subscribe} "
                               f"(id={pk})"
                },
                status=status.HTTP_200_OK,
            )
        user.my_subscriptions.add(user_to_subscribe)
        user_to_subscribe.followers.add(user)
        return Response(
            data={"message": f"Subscribed from {user_to_subscribe} (id={pk})"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["GET"],
        url_path="unsubscribe",
        url_name="unsubscribe",
        permission_classes=[IsAuthenticated],
    )
    def unsubscribe(self, request: HttpRequest, pk: int = None) -> Response:
        user = self.request.user
        user_to_unsubscribe = get_object_or_404(User, pk=pk)
        if user_to_unsubscribe not in user.my_subscriptions.all():
            return Response(
                data={
                    "message": f"Not followed from {user_to_unsubscribe} "
                               f"(id={pk})"
                },
                status=status.HTTP_200_OK,
            )
        user.my_subscriptions.remove(user_to_unsubscribe)
        user_to_unsubscribe.followers.remove(user)
        return Response(
            data={
                "message": f"Unsubscribed from {user_to_unsubscribe} (id={pk})"
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["GET"],
        url_path="my-posts",
        url_name="my-posts",
        permission_classes=[IsAuthenticated],
    )
    def my_posts(self, request: HttpRequest, pk: int = None) -> Response:
        user = self.request.user
        posts = Post.objects.filter(owner=user).annotate(
            comments_count=Count("comments"), likes_count=Count("likes")
        )
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        url_path="my-subscriptions-posts",
        url_name="my-subscriptions-posts",
        permission_classes=[IsAuthenticated],
    )
    def my_subscriptions_posts(
        self, request: HttpRequest, pk: int = None
    ) -> Response:
        user = self.request.user
        posts = Post.objects.filter(
            owner__in=user.my_subscriptions.all()
        ).annotate(
            comments_count=Count("comments"), likes_count=Count("likes")
        )
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        url_path="licked-posts",
        url_name="liked-posts",
        permission_classes=[IsAuthenticated],
    )
    def liked_posts(self, request: HttpRequest, pk: int = None) -> Response:
        user = self.request.user
        posts = Post.objects.filter(likes=user).annotate(
            comments_count=Count("comments"), likes_count=Count("likes")
        )
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve current user",
        tags=["Users"],
        description="Retrieve the details of the current authenticated user.",
        responses={
            200: UserManageSerializer,
        },
    ),
    put=extend_schema(
        summary="Update current user",
        description="Update the details of the current authenticated user.",
        tags=["Users"],
        responses={
            200: UserUpdateSerializer,
        },
    ),
    patch=extend_schema(
        summary="Partially update current user",
        description="Partially update the details of the current "
                    "authenticated user.",
        tags=["Users"],
        responses={
            200: UserUpdateSerializer,
        },
    ),
    delete=extend_schema(
        summary="Delete current user",
        description="Delete the current authenticated user.",
        tags=["Users"],
        responses={
            204: OpenApiResponse(description="No Content"),
        },
    ),
)
class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited without a password.
    """

    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        return (
            User.objects.all()
            .filter(id=user.id)
            .select_related("residence_place")
        )

    def get_object(self) -> User:
        return self.request.user

    def get_serializer_class(self) -> Type[Serializer]:
        if self.request.method == "GET":
            return UserManageSerializer
        return UserUpdateSerializer


@extend_schema_view(
    put=extend_schema(
        summary="Update user password",
        description="Update the password of the current authenticated user.",
        tags=["Users"],
        responses={
            200: OpenApiResponse(description="Password updated successfully"),
        },
    ),
    patch=extend_schema(
        summary="Partially update user password",
        description="Partially update the password of the current "
                    "authenticated user.",
        tags=["Users"],
        responses={
            200: OpenApiResponse(description="Password updated successfully"),
        },
    ),
)
class UserPasswordUpdateView(generics.UpdateAPIView):
    """
    API endpoint that allows users update their password.
    """

    serializer_class = UserPasswordUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> User:
        return self.request.user
