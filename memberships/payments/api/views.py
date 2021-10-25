from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from memberships.payments.api.serializers import (
    PaymentProcessingSerializer,
    PaymentSerializer,
    PayoutSerializer,
)
from memberships.payments.models import Payment


class PaymentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        # include recently failed?
        return self.request.user.payments.filter(status=Payment.Status.CAPTURED)

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentProcessingSerializer
        return super().get_serializer_class()


class PayoutViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PayoutSerializer

    def get_queryset(self):
        return self.request.user.payouts.all()
