from django.db.models import Q, Sum
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from memberships.payments.models import Payment

from memberships.subscriptions.api.serializers import (
    MemberSerializer,
    MembershipSerializer,
    SubscriptionSerializer,
    TierSerializer,
)
from memberships.subscriptions.models import Membership, Subscription
from memberships.users.api.permissions import IsCreator


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

    def get_queryset(self):
        queryset = Membership.objects.exclude(is_active__isnull=True).filter(
            Q(creator_user=self.request.user.pk) | Q(fan_user=self.request.user.pk)
        )
        if creator_username := self.request.query_params.get("creator_username"):
            queryset = queryset.filter(creator_user__username__iexact=creator_username)

        if fan_username := self.request.query_params.get("fan_username"):
            queryset = queryset.filter(fan_user__username__iexact=fan_username)

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
