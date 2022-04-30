from django.db.models import Q
from rest_framework import mixins, permissions, viewsets

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from memberships.payments.api.filters import PaymentFilter

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
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = PaymentFilter
    ordering_fields = ["created_at", "amount"]
    search_fields = ["fan_user__email", "fan_user__name"]

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
