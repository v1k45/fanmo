from django.db.models.signals import post_save
from django.dispatch import receiver

from fanmo.payments.models import BankAccount
from fanmo.users.models import SocialLink, User, UserOnboarding, UserPreference


@receiver(post_save, sender=User)
def create_user_relations(sender, instance, created, *args, **__):
    if created:
        SocialLink.objects.create(user=instance)
        UserPreference.objects.create(user=instance)
        UserOnboarding.objects.create(user=instance)


@receiver(post_save, sender=UserOnboarding)
def sync_bank_account_status_with_onboarding_status(sender, instance, *args, **__):
    if instance.status == UserOnboarding.Status.SUBMITTED:
        BankAccount.objects.filter(beneficiary_user=instance.user).update(
            status=BankAccount.Status.PROCESSING
        )
