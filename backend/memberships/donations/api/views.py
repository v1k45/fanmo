from rest_framework import mixins, viewsets

from memberships.donations.api.serializers import (
    DonationCreateSerializer,
    DonationSerializer,
    DonationUpdateSerializer,
)
from memberships.donations.models import Donation


# protect this view
class DonationViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    def get_queryset(self):
        queryset = Donation.objects.filter(status=Donation.Status.SUCCESSFUL)
        username = self.request.query_params.get("username")
        if username:
            return queryset.filter(creator_user__username__iexact=username)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return DonationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return DonationUpdateSerializer
        return DonationSerializer
