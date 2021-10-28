from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from memberships.subscriptions.api.serializers import (
    SubscriberSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    TierSerializer,
)


class TierViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    serializer_class = TierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.tiers.all()


class SubscriptionViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscriptions.all()

    def get_serializer_class(self):
        if self.action == "create":
            return SubscriptionCreateSerializer
        return SubscriptionSerializer

    # do we need pause/resume?
    @extend_schema(request=None)
    @action(methods=["POST"], detail=True)
    def pause(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.pause()
        subscription.save()
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(methods=["POST"], detail=True)
    def resume(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.resume()
        subscription.save()
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(methods=["POST"], detail=True)
    def cancel(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.cancel()
        subscription.save()
        return self.retrieve(request, *args, **kwargs)


class SubscriberViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscribers.all()
