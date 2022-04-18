from django.db.models import Q
from rest_framework import mixins, permissions, viewsets

from memberships.payments.api.serializers import (
    BankAccountSerializer,
    PaymentProcessingSerializer,
    PaymentSerializer,
    PayoutSerializer,
)
from memberships.payments.models import Payment, Payout


class PaymentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Payment.objects.filter(status=Payment.Status.CAPTURED)

    def get_permissions(self):
        # accept payments anonymously
        if self.action == "create":
            return []
        return super().get_permissions()

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(Q(creator_user=self.request.user) | Q(fan_user=self.request.user))
        )

        if membership_id := self.request.query_params.get("membership_id"):
            queryset = queryset.filter(subscription__membership_id=membership_id)

        if donor_username := self.request.query_params.get("donor_username"):
            queryset = queryset.filter(donation__fan_user__username=donor_username)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentProcessingSerializer
        return super().get_serializer_class()


class PayoutViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payout.objects.filter(payment__creator_user=self.request.user).all()


class BankAccountViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    # todo: don't allow more than one account
    # todo: don't allow updating account
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.bank_accounts.all()
