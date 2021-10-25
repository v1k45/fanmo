from rest_framework import viewsets, mixins

from memberships.donations.api.serializers import (
    DonationCreateSerializer,
    DonationSerializer,
)

# protect this view
class DonationViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return self.request.user.donations.all()

    def get_serializer_class(self):
        if self.action == "create":
            return DonationCreateSerializer
        return DonationSerializer
