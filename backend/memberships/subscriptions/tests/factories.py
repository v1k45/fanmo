from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory.django import DjangoModelFactory


class TierFactory(DjangoModelFactory):
    name = Faker("name")
