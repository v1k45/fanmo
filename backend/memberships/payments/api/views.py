from rest_framework import mixins, viewsets, permissions
from memberships.payments.api.serializers import (
    BankAccountSerializer,
    PaymentProcessingSerializer,
    PaymentSerializer,
    PayoutSerializer,
)
from memberships.payments.models import Payment


class PaymentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # include recently failed?
        return self.request.user.payments.filter(status=Payment.Status.CAPTURED)

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentProcessingSerializer
        return super().get_serializer_class()


class PayoutViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.payouts.all()


class BankAccountViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.bank_accounts.all()