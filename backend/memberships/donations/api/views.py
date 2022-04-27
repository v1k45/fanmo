from rest_framework import mixins, viewsets
from django.db.models import Sum, Q, F

from memberships.donations.api.serializers import (
    DonationCreateSerializer,
    DonationSerializer,
    DonationUpdateSerializer,
)
from memberships.donations.models import Donation
from memberships.payments.models import Payment


class DonationViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    def get_queryset(self):
        queryset = Donation.objects.filter(status=Donation.Status.SUCCESSFUL)
        # filter by creator username
        if creator_username := self.request.query_params.get("creator_username"):
            queryset = queryset.filter(creator_user__username__iexact=creator_username)

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
        return queryset

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
        return DonationSerializer
