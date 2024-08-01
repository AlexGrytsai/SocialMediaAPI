from django.db import transaction
from rest_framework import serializers

from post.models import Post, Hashtag


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ["tag"]


class PostSerializer(serializers.ModelSerializer):
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
            "id",
            "title",
            "text",
            "image",
            "hashtags",
            "add_new_hashtags",
        ]

        kwargs = {
            "image": {
                "required": False,
            },
        }

    def create(self, validated_data: dict) -> Post:
        user = self.context["request"].user
        with transaction.atomic():
            add_hashtag = validated_data.pop("add_new_hashtags", [])
            hashtags = validated_data.pop("hashtags", [])
            post = Post.objects.create(**validated_data, owner=user)
            if add_hashtag:
                for hashtag in add_hashtag:
                    tag, _ = Hashtag.objects.get_or_create(tag=hashtag["tag"])
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
            return instance
