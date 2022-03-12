from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action

from memberships.subscriptions.api.serializers import (
    MemberSerializer,
    MembershipSerializer,
    SubscriberSerializer,
    SubscriptionCreateSerializer,
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
        return self.request.user.members.exclude(is_active__isnull=True)


class MembershipViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = MembershipSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Membership.objects.none()
        queryset = self.request.user.memberships.all().exclude(is_active__isnull=True)
        return queryset.select_related(
            "fan_user",
            "creator_user",
            "tier",
            "active_subscription",
            "scheduled_subscription",
        )

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, *args, **kwargs):
        membership = self.get_object()
        membership.cancel()
        return self.retrieve(*args, **kwargs)


class SubscriptionViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscriptions.exclude(
            status=Subscription.Status.CREATED
        )

    def get_serializer_class(self):
        if self.action == "create":
            return SubscriptionCreateSerializer
        return SubscriptionSerializer

    @extend_schema(request=None)
    @action(methods=["POST"], detail=True)
    def cancel(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.schedule_to_cancel()
        subscription.save()
        return self.retrieve(request, *args, **kwargs)


class SubscriberViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscribers.exclude(
            status=Subscription.Status.CREATED
        ).all()
