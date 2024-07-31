from __future__ import annotations

import os
import uuid

from django.db import models

from users.models import User


class Hashtag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        primary_key=True,
        db_comment="The unique name of the hashtag",
        help_text="Enter the unique name of the hashtag"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["-name"]),
        ]


class Comment(models.Model):
    text = models.TextField(
        max_length=300,
        db_comment="The content of the comment",
        help_text="Enter the content of the comment, up to 300 characters"
    )
    created_date = models.DateField(
        auto_now_add=True,
        db_comment="The date when the comment was created",
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return f"Comment: {self.text} ({self.owner})"


class Like(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="likes"
    )

    def __str__(self):
        return f"Like: {self.owner}"


def create_custom_path_for_image(instance: Post, filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return (f"users-photos/{instance.owner.email}/posts/"
            f"{uuid.uuid4()}{extension}")


class Post(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
        db_comment="The title of the post",
        help_text="Enter the title of the post, up to 100 characters"
    )
    text = models.TextField(
        max_length=3000,
        db_comment="The content of the post",
        help_text="Enter the content of the post, up to 3000 characters"
    )
    image = models.ImageField(
        upload_to=create_custom_path_for_image,
        null=True,
        blank=True,
        db_comment="The image associated with the post",
        help_text="Upload an image to be associated with the post"
    )
    created_date = models.DateField(
        auto_now_add=True, db_comment="The date when the post was created"
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    hashtags = models.ManyToManyField(Hashtag, related_name="posts")
    likes = models.ManyToManyField(Like, related_name="posts")
    comments = models.ManyToManyField(Comment, related_name="posts")

    def __str__(self):
        return f"Post: {self.title} ({self.owner})"

    def clean(self):
        if self.image:
            max_image_size = 2097152
            if self.image.size > max_image_size:
                raise ValueError(
                    f"Photo size should be less than "
                    f"{max_image_size / 1024 / 1024}MB"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["title"]),
        ]
