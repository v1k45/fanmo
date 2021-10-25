from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from memberships.users.models import User

from .serializers import UserSerializer

from drf_spectacular.utils import extend_schema


class UserViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self):
        return super().get_queryset()

    @extend_schema(request=None)
    @action(detail=True, methods=["POST"])
    def follow(self, request, *args, **kwargs):
        user = self.get_object()
        self.request.user.follow(user)
        return self.detail(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(detail=True, methods=["POST"])
    def unfollow(self, request, *args, **kwargs):
        user = self.get_object()
        self.request.user.unfollow(user)
        return self.detail(request, *args, **kwargs)

    @action(detail=True, methods=["GET"])
    def followers(self, request, *args, **kwargs):
        pass

    @action(detail=True, methods=["GET"])
    def followings(self, request, *args, **kwargs):
        pass


class OwnUserAPIView(RetrieveModelMixin, UpdateModelMixin, GenericAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
