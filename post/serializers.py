import os
from urllib.request import urlopen

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from post.models import (
    Post,
    Hashtag,
    Comment
)
from post.tasks import create_scheduled_post


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ["tag"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["text"]

    def create(self, validated_data: dict, **args) -> Comment:
        pk = self.context["request"].parser_context["kwargs"]["pk"]
        post = get_object_or_404(Post, pk=pk)
        comment = Comment.objects.create(
            **validated_data, owner=self.context["request"].user
        )
        post.comments.add(comment)
        return comment

    def update(self, instance: Comment, validated_data: dict) -> Comment:
        instance.text = validated_data.get("text", instance.text)
        instance.save()
        return instance


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="owner")

    class Meta:
        model = Comment
        fields = [
            "id",
            "text",
            "author",
            "created_date",
        ]


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    This serializer is used to create and update Post instances.
    It also handles the creation and updating of associated Hashtags.
    """

    hashtags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Hashtag.objects.all(),
        required=False,
    )
    add_new_hashtags = HashtagSerializer(
        many=True,
        required=False,
        read_only=False,
        allow_null=True
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "text",
            "image",
            "hashtags",
            "add_new_hashtags",
            "scheduled_date"
        ]

        kwargs = {
            "image": {
                "required": False,
            },
        }

    def to_internal_value(self, data: dict) -> dict:
        mutable_data = data.copy()
        if "image" in mutable_data and mutable_data["image"] == "":
            mutable_data["image"] = None
        if (
            "image" in mutable_data
            and isinstance(mutable_data["image"], str)
            and mutable_data["image"].startswith("http")
        ):
            try:
                response = urlopen(data["image"])
                file_name = os.path.basename(data["image"])
                mutable_data["image"] = ContentFile(
                    response.read(), name=file_name
                )
            except Exception:
                raise serializers.ValidationError(
                    {"image": "Error downloading image."}
                )
        return super().to_internal_value(mutable_data)

    def create(self, validated_data: dict) -> Post:
        user = self.context["request"].user
        add_hashtag = validated_data.pop("add_new_hashtags", [])
        hashtags = validated_data.pop("hashtags", [])
        scheduled_date = validated_data.pop("scheduled_date", None)
        if scheduled_date:
            print(f"scheduled date: {scheduled_date}")
            hashtag_tags = [hashtag.tag for hashtag in hashtags]
            create_scheduled_post.apply_async(
                kwargs={
                    "title": validated_data["title"],
                    "text": validated_data["text"],
                    "image": validated_data["image"],
                    "owner_id": user.id,
                    "hashtags": hashtag_tags,
                    "add_hashtag": add_hashtag
                },
                eta=scheduled_date,
            )
            placeholder_post = Post(
                title=validated_data["title"],
                text=validated_data["text"],
                owner=user,
                image=validated_data.get("image"),
                scheduled_date=scheduled_date
            )
            placeholder_post.id = None
            return placeholder_post
        else:
            with transaction.atomic():
                post = Post.objects.create(**validated_data, owner=user)
                if add_hashtag:
                    for hashtag in add_hashtag:
                        tag, _ = Hashtag.objects.get_or_create(
                            tag=hashtag["tag"])
                        post.hashtags.add(tag)
                if hashtags:
                    for hashtag in hashtags:
                        post.hashtags.add(hashtag)
                return post

    def update(self, instance: Post, validated_data: dict) -> Post:
        with transaction.atomic():
            add_hashtag = validated_data.pop("add_new_hashtags", [])
            hashtags = validated_data.pop("hashtags", [])
            instance = super().update(instance, validated_data)
            instance.hashtags.clear()
            if add_hashtag:
                for hashtag in add_hashtag:
                    tag, _ = Hashtag.objects.get_or_create(tag=hashtag["tag"])
                    instance.hashtags.add(tag)
            if hashtags:
                for hashtag in hashtags:
                    instance.hashtags.add(hashtag)
        if validated_data["image"]:
            old_name_image = os.path.basename(instance.image.name)
            new_name_image = validated_data["image"].name
            if old_name_image == new_name_image:
                validated_data.pop("image")
        return instance


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="owner")
    comments_count = serializers.IntegerField()
    likes_count = serializers.IntegerField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "hashtags",
            "comments_count",
            "likes_count"
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="owner")
    comments = CommentListSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField()
    who_liked = serializers.StringRelatedField(
        source="likes", many=True, read_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "text",
            "author",
            "image",
            "created_date",
            "hashtags",
            "likes_count",
            "comments",
            "who_liked"
        ]
