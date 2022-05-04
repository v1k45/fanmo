from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from django.db.models import Sum, Q, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from memberships.donations.api.serializers import (
    DonationCreateSerializer,
    DonationSerializer,
    DonationUpdateSerializer,
    PublicDonationSerializer,
)
from memberships.donations.models import Donation
from memberships.payments.models import Payment
from memberships.donations.api.filters import DonationFilter


class DonationViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = DonationFilter
    ordering_fields = ["created_at", "amount", "lifetime_amount"]

    def get_queryset(self):
        queryset = Donation.objects.filter(status=Donation.Status.SUCCESSFUL)
        queryset = queryset.annotate(
            lifetime_amount=Sum(
                "fan_user__payments__amount",
                filter=Q(
                    fan_user__payments__status=Payment.Status.CAPTURED,
                    fan_user__payments__type=Payment.Type.DONATION,
                    fan_user__payments__creator_user_id=F("creator_user_id"),
                ),
            )
        )
        if self.action != "recent":
            queryset = queryset.filter(
                Q(creator_user=self.request.user.pk) | Q(fan_user=self.request.user.pk)
            )
        return queryset.order_by("-created_at")

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        if self.action == "recent":
            # only include first 30 donations
            return qs[:30]
        return qs

    @property
    def search_fields(self):
        if self.action == "recent":
            return []
        elif "creator_username" in self.request.query_params:
            return ["fan_user__name", "fan_user__email"]
        elif "fan_username" in self.request.query_params:
            return ["creator_user__name", "creator_user__email"]
        return []

    @action(methods=["get"], detail=False)
    def recent(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if (
            self.action in ["update", "partial_update"]
            and obj.creator_user_id != self.request.user.pk
        ):
            self.permission_denied(request)

    def get_serializer_class(self):
        if self.action == "create":
            return DonationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return DonationUpdateSerializer
        elif self.action == "recent":
            return PublicDonationSerializer
        return DonationSerializer
