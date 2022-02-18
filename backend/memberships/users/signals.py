from django.db.models.signals import post_save
from django.dispatch import receiver

from memberships.users.models import SocialLink, User, UserOnboarding, UserPreference


@receiver(post_save, sender=User)
def create_user_relations(sender, instance, created, *args, **__):
    if created:
        SocialLink.objects.create(user=instance)
        UserPreference.objects.create(user=instance)
        UserOnboarding.objects.create(user=instance)
