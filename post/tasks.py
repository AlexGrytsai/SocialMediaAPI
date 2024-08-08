import logging

from celery import shared_task
from django.contrib.auth.models import User
from django.db import transaction

from post.models import Post, Hashtag

logger = logging.getLogger(__name__)


@shared_task
def create_scheduled_post(
    title: str,
    text: str,
    image: str,
    owner_id: int,
    hashtags: list,
    add_hashtag: list,
) -> None:
    try:
        with transaction.atomic():
            logger.info("Creating scheduled post with title: %s", title)
            owner = User.objects.get(id=owner_id)
            post = Post.objects.create(
                title=title, text=text, image=image, owner=owner
            )
            if add_hashtag:
                for hashtag in add_hashtag:
                    tag, _ = Hashtag.objects.get_or_create(tag=hashtag["tag"])
                    post.hashtags.add(tag)
            if hashtags:
                for hashtag in hashtags:
                    post.hashtags.add(hashtag)
            logger.info("Post created successfully")
    except Exception as e:
        logger.error("Error creating post: %s", str(e))
        raise
