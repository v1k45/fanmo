from decimal import Decimal
from django.contrib.auth import get_user_model
from factory import Faker, post_generation, SubFactory
from factory.django import DjangoModelFactory

from memberships.subscriptions.models import Membership, Tier, Plan, Subscription
from moneyed import Money


class TierFactory(DjangoModelFactory):
    name = Faker("name")
    amount = Money(amount=Decimal(100), currency="INR")
    benefits = ["Membership!"]

    class Meta:
        model = Tier


class PlanFactory(DjangoModelFactory):
    name = Faker("name")
    tier = SubFactory(TierFactory)
    external_id = Faker("uuid4")
    amount = Money(amount=Decimal(100), currency="INR")

    class Meta:
        model = Plan
        django_get_or_create = ["tier"]


class SubscriptionFactory(DjangoModelFactory):
    plan = SubFactory(PlanFactory)
    payment_method = Subscription.PaymentMethod.CARD
    external_id = Faker("uuid4")

    class Meta:
        model = Subscription


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = Membership
