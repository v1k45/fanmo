from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from fanmo.donations.api.filters import DonationFilter
from fanmo.donations.api.serializers import (
    DonationCreateSerializer,
    DonationReactionSerializer,
    DonationSerializer,
    DonationSocialStatsSerializer,
    DonationStatsSerializer,
    DonationUpdateSerializer,
    PublicDonationSerializer,
)
from fanmo.donations.exports import DonationExportResource
from fanmo.donations.models import Donation
from fanmo.payments.models import Payment
from fanmo.users.api.permissions import IsCreator
from fanmo.utils.throttling import Throttle


class DonationViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = DonationFilter
    ordering_fields = ["created_at", "amount", "lifetime_amount"]
    throttle_classes = [Throttle("transaction_hour", "create")]

    def get_queryset(self):
        queryset = Donation.objects.filter(
            status=Donation.Status.SUCCESSFUL
        ).select_related("fan_user", "post", "creator_user__user_preferences")
        queryset = queryset.prefetch_related("reactions")
        queryset = queryset.annotate(
            lifetime_amount=Sum(
                "fan_user__payments__amount",
                filter=Q(
                    fan_user__payments__status=Payment.Status.CAPTURED,
                    fan_user__payments__type=Payment.Type.DONATION,
                    fan_user__payments__creator_user_id=F("creator_user_id"),
                ),
                distinct=True,
            ),
            comment_count=Count(
                "comments", filter=Q(comments__is_published=True), distinct=True
            ),
        )
        if self.action not in ["recent", "reactions"]:
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

    def get_serializer_class(self):
        if self.action == "create":
            return DonationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return DonationUpdateSerializer
        elif self.action == "recent":
            return PublicDonationSerializer
        elif self.action == "stats":
            return DonationStatsSerializer
        elif self.action == "reactions":
            return DonationReactionSerializer
        return DonationSerializer

    @property
    def search_fields(self):
        if self.action == "recent":
            return []
        elif "creator_username" in self.request.query_params:
            return ["fan_user__name", "fan_user__email"]
        elif "fan_username" in self.request.query_params:
            return ["creator_user__name", "creator_user__email"]
        return []

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if (
            self.action in ["update", "partial_update"]
            and obj.creator_user_id != self.request.user.pk
        ):
            self.permission_denied(request)

    @action(methods=["get"], detail=False)
    def recent(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

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
                total_with_message=Count("id", filter=Q(message="")),
                total_without_message=Count("id", filter=~Q(message="")),
                total_payment=Coalesce(Sum("amount"), Decimal(0)),
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
        return DonationExportResource().export_csv(queryset)

    @extend_schema(responses=DonationSocialStatsSerializer)
    @action(
        detail=True, permission_classes=[permissions.IsAuthenticated], methods=["POST"]
    )
    def reactions(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self.request.data, instance=self.get_object()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = DonationSocialStatsSerializer(
            self.get_object(), context=self.get_serializer_context()
        )
        return Response(response_serializer.data)
