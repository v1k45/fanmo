from django.db.models.signals import post_save
from django.dispatch import receiver

from fanmo.payments.models import BankAccount
from fanmo.users.models import UserOnboarding


@receiver(post_save, sender=BankAccount)
def sync_payment_added_with_new_bank_account(sender, instance, created, *args, **__):
    if created:
        UserOnboarding.objects.filter(user=instance.beneficiary_user).update(
            is_bank_account_added=True
        )
