from decimal import Decimal

from django.contrib.auth import get_user_model
from djmoney.money import Money
from factory import Faker, SubFactory, post_generation
from factory.django import DjangoModelFactory
from moneyed import INR

from fanmo.memberships.models import Membership, Plan, Subscription, Tier


class TierFactory(DjangoModelFactory):
    name = Faker("name")
    amount = Money(Decimal(100), INR)
    benefits = ["Membership!"]

    class Meta:
        model = Tier


class PlanFactory(DjangoModelFactory):
    name = Faker("name")
    tier = SubFactory(TierFactory)
    external_id = Faker("uuid4")
    amount = Money(Decimal(100), INR)
    period = Plan.Period.MONTHLY

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
