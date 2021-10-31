from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory

from memberships.payments.models import BankAccount


class BankAccountFactory(DjangoModelFactory):
    account_name = Faker("user_name")
    account_number = Faker("iban")
    beneficiary_name = Faker("user_name")
    ifsc = Faker("swift")
    status = BankAccount.Status.LINKED

    class Meta:
        model = BankAccount
