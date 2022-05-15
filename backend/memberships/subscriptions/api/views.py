from copy import deepcopy
from telnetlib import DO
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, Count
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from memberships.donations.models import Donation
from memberships.payments.models import Payment, Payout
from django.utils import timezone
from dateutil.rrule import rrule, DAILY

from memberships.subscriptions.api.serializers import (
    MemberSerializer,
    MembershipGiveawaySerializer,
    MembershipSerializer,
    MemebershipStatsSerializer,
    SubscriptionSerializer,
    TierSerializer,
)
from memberships.subscriptions.models import Membership, Subscription
from memberships.users.api.permissions import IsCreator
from memberships.subscriptions.api.filters import MembershipFilter


class TierViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    serializer_class = TierSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreator]

    def get_queryset(self):
        return self.request.user.tiers.all()


class MembersViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MemberSerializer

    def get_queryset(self):
        queryset = self.request.user.members.exclude(is_active__isnull=True)
        queryset = queryset.select_related(
            "fan_user",
            "creator_user",
            "tier",
            "active_subscription",
            "scheduled_subscription",
        )
        queryset = queryset.annotate(
            lifetime_amount=Sum(
                "subscriptions__payments__amount",
                filter=Q(subscriptions__payments__status=Payment.Status.CAPTURED),
            )
        )
        return queryset

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, *args, **kwargs):
        membership = self.get_object()
        membership.cancel()
        return self.retrieve(*args, **kwargs)


class MembershipViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    """
    TODO: Test and fix concurrent membership requests.
    """

    serializer_class = MembershipSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = MembershipFilter
    ordering_fields = ["created_at", "lifetime_amount"]

    @property
    def search_fields(self):
        if "creator_username" in self.request.query_params:
            return ["fan_user__name", "fan_user__email"]
        elif "fan_username" in self.request.query_params:
            return ["creator_user__name", "creator_user__email"]
        return []

    def get_queryset(self):
        queryset = Membership.objects.exclude(is_active__isnull=True).filter(
            Q(creator_user=self.request.user.pk) | Q(fan_user=self.request.user.pk)
        )

        queryset = queryset.select_related(
            "fan_user",
            "creator_user",
            "tier",
            "active_subscription",
            "scheduled_subscription",
        )
        queryset = queryset.annotate(
            lifetime_amount=Sum(
                "subscriptions__payments__amount",
                filter=Q(subscriptions__payments__status=Payment.Status.CAPTURED),
            )
        )
        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "stats":
            return MemebershipStatsSerializer
        elif self.action == "giveaway":
            return MembershipGiveawaySerializer
        return super().get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        if self.action == "giveaway":
            kwargs.update({"many": True})
        return super().get_serializer(*args, **kwargs)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated, IsCreator),
        methods=["post"],
    )
    def giveaway(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, *args, **kwargs):
        membership = self.get_object()
        membership.cancel()
        return self.retrieve(*args, **kwargs)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsCreator],
    )
    def stats(self, *args, **kwargs):
        agg_stats = (
            self.get_queryset()
            .filter(creator_user=self.request.user.pk)
            .aggregate(
                total=Count("id"),
                active=Count("id", filter=Q(is_active=True)),
                inactive=Count("id", filter=Q(is_active=False)),
                total_payment=Sum("lifetime_amount"),
            )
        )
        return Response(self.get_serializer(agg_stats).data)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.exclude(status=Subscription.Status.CREATED)

    def get_queryset(self):
        # find subscriptions for or by the currently authenticated user
        user = self.request.user
        queryset = (
            super()
            .get_queryset()
            .filter(Q(membership__creator_user=user) | Q(membership__fan_user=user))
        )
        # filter by membership id
        if membership_id := self.request.query_params.get("membership_id"):
            queryset = queryset.filter(membership_id=membership_id)

        queryset = queryset.select_related("plan__tier")
        return queryset


class CreatorStatsAPIView(viewsets.GenericViewSet):
    def list(self, *args, **kwargs):
        now = timezone.now().replace(hour=23, minute=59, second=59)
        then = now - relativedelta(days=7)
        user = self.request.user

        current_active_memberships = (
            Subscription.objects.active_at(now).filter(creator_user=user).count()
        )
        last_active_memberships = (
            Subscription.objects.active_at(then).filter(creator_user=user).count()
        )

        current_donation_count = Donation.objects.filter(
            creator_user=user, status=Donation.Status.SUCCESSFUL, created_at__lte=now
        ).count()
        last_donation_count = Donation.objects.filter(
            creator_user=user, status=Donation.Status.SUCCESSFUL, created_at__lte=then
        ).count()

        current_payment_amount = (
            Payment.objects.filter(creator_user=user, status=Payment.Status.CAPTURED)
            .filter(created_at__lte=now)
            .aggregate(
                total_amount=Sum("amount"),
                donation_amount=Sum("amount", filter=Q(type=Payment.Type.DONATION)),
                subscription_amount=Sum(
                    "amount", filter=Q(type=Payment.Type.SUBSCRIPTION)
                ),
            )
        )
        last_payment_amount = (
            Payment.objects.filter(creator_user=user, status=Payment.Status.CAPTURED)
            .filter(created_at__lte=then)
            .aggregate(
                total_amount=Sum("amount"),
                donation_amount=Sum("amount", filter=Q(type=Payment.Type.DONATION)),
                subscription_amount=Sum(
                    "amount", filter=Q(type=Payment.Type.SUBSCRIPTION)
                ),
            )
        )

        current_payout_amount = (
            Payout.objects.filter(payment__creator_user=user)
            .filter(created_at__lte=now)
            .aggregate(
                total_amount=Sum("amount"),
                donation_amount=Sum(
                    "amount", filter=Q(payment__type=Payment.Type.DONATION)
                ),
                subscription_amount=Sum(
                    "amount", filter=Q(payment__type=Payment.Type.SUBSCRIPTION)
                ),
            )
        )
        last_payout_amount = (
            Payout.objects.filter(payment__creator_user=user)
            .filter(created_at__lte=then)
            .aggregate(
                total_amount=Sum("amount"),
                donation_amount=Sum(
                    "amount", filter=Q(payment__type=Payment.Type.DONATION)
                ),
                subscription_amount=Sum(
                    "amount", filter=Q(payment__type=Payment.Type.SUBSCRIPTION)
                ),
            )
        )

    def get_stats(self, till_date, period):
        summary_stats = {
            "subscription_count": 0,
            "donation_count": 0,
            "total_payment_amount": 0,
            "donation_payment_amount": 0,
            "subscription_payment_amount": 0,
            "total_payout_amount": 0,
        }

        user = self.request.user

        stats_data_by_date = {}
        for date in rrule.between(
            till_date, till_date + relativedelta(weeks=1), inc=True
        ):
            stats_data_by_date.setdefault(date, deepcopy(summary_stats))

        active_memberships = (
            Subscription.objects.active_at(till_date)
            .filter(creator_user=user)
            .values("cycle_start_at", "cycle_end_at")
        )
        for active_membership in active_memberships:
            current_date = active_membership["cycle_start_at"].date().isoformat()

            for date in rrule(DAILY).between(
                active_membership["cycle_end_at"],
                active_membership["cycle_start_at"],
                DAILY,
                inc=True,
            ):
                stats_data_by_date.setdefault(
                    date.date().isoformat(), deepcopy(summary_stats)
                )

        current_active_memberships = (
            Subscription.objects.active_at(till_date).filter(creator_user=user).count()
        )
        current_donation_count = Donation.objects.filter(
            creator_user=user, status=Donation.Status.SUCCESSFUL, created_at__lte=now
        ).count()
        current_payment_amount = (
            Payment.objects.filter(creator_user=user, status=Payment.Status.CAPTURED)
            .filter(created_at__lte=now)
            .aggregate(
                total_amount=Sum("amount"),
                donation_amount=Sum("amount", filter=Q(type=Payment.Type.DONATION)),
                subscription_amount=Sum(
                    "amount", filter=Q(type=Payment.Type.SUBSCRIPTION)
                ),
            )
        )
        current_payout_amount = (
            Payout.objects.filter(payment__creator_user=user)
            .filter(created_at__lte=now)
            .aggregate(
                total_amount=Sum("amount"),
                donation_amount=Sum(
                    "amount", filter=Q(payment__type=Payment.Type.DONATION)
                ),
                subscription_amount=Sum(
                    "amount", filter=Q(payment__type=Payment.Type.SUBSCRIPTION)
                ),
            )
        )
