from fanmo.core.tasks import async_task
from fanmo.users.models import User
from fanmo.utils.images import generate_page_summary


def refresh_user_social_image(creator_user_id):
    user = User.objects.get(pk=creator_user_id)
    if not user.is_creator:
        return

    user.social_image.save(f"user_{creator_user_id}.jpg", generate_page_summary(user))


def refresh_all_user_social_images():
    for user_id in User.objects.filter(is_creator=True).values_list("id", flat=True):
        async_task(refresh_user_social_image, user_id)
