from fanmo.core.tasks import async_task
from fanmo.posts.models import Post
from fanmo.utils.images import generate_post_summary


def refresh_post_social_image(post_id):
    post = (
        Post.objects.select_related("content", "author_user")
        .prefetch_related("content__files")
        .get(pk=post_id)
    )
    post.social_image.save(f"post_{post_id}.jpg", generate_post_summary(post))


def refresh_all_post_social_images():
    for post_id in Post.objects.filter(is_published=True).values_list("id", flat=True):
        async_task(refresh_post_social_image, post_id)
