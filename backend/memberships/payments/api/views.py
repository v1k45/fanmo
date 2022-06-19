from django.db.models import Q, Sum, Count
from rest_framework.response import Response
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from memberships.payments.exports import PaymentExportResource
from memberships.payments.api.filters import PaymentFilter

from memberships.users.api.permissions import IsCreator
from memberships.payments.api.serializers import (
    BankAccountSerializer,
    PaymentProcessingSerializer,
    PaymentSerializer,
    PaymentStatsSerializer,
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
        elif self.action == "stats":
            return PaymentStatsSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsCreator],
    )
    def stats(self, *args, **kwargs):
        agg_stats = (
            self.get_queryset()
            .filter(creator_user=self.request.user.pk)
            .aggregate(
                total=Count("id"),
                total_amount=Sum("amount"),
                total_payout_scheduled=Sum(
                    "payout__amount", filter=Q(payout__status=Payout.Status.SCHEDULED)
                ),
                total_payout_processed=Sum(
                    "payout__amount", filter=Q(payout__status=Payout.Status.PROCESSED)
                ),
            )
        )
        return Response(self.get_serializer(agg_stats).data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsCreator],
    )
    def export(self, *args, **kwargs):
        queryset = self.get_queryset().filter(creator_user=self.request.user)
        return PaymentExportResource().export_csv(queryset)


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
