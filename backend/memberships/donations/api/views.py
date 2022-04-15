from rest_framework import mixins, viewsets

from memberships.donations.api.serializers import (
    DonationCreateSerializer,
    DonationSerializer,
    DonationUpdateSerializer,
)
from memberships.donations.models import Donation


class DonationViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    def get_queryset(self):
        queryset = Donation.objects.filter(status=Donation.Status.SUCCESSFUL)
        # filter by creator username
        if creator_username := self.request.query_params.get("creator_username"):
            queryset = queryset.filter(creator_user__username__iexact=creator_username)
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
