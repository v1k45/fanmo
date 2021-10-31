from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from memberships.users.models import User

from .serializers import UserSerializer

from drf_spectacular.utils import extend_schema


class UserViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    # only show active?
    queryset = User.objects.all()
    lookup_field = "username"

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

    # create a nested viewset
    @action(detail=True, methods=["GET"])
    def followers(self, request, *args, **kwargs):
        pass

    @action(detail=True, methods=["GET"])
    def followings(self, request, *args, **kwargs):
        pass


class OwnUserAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
