from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory

from fanmo.payments.models import BankAccount


class BankAccountFactory(DjangoModelFactory):
    account_name = Faker("user_name")
    account_number = Faker("iban")
    ifsc = Faker("swift")
    status = BankAccount.Status.CREATED
    external_id = Faker("iban")

    class Meta:
        model = BankAccount
