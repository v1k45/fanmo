from rest_framework.permissions import BasePermission


class IsCreator(BasePermission):
    """
    Allows access only to creator users.
    """

    message = "Only creators are allowed to perform this action."
    code = "creator_required"

    def has_permission(self, request, view):
        return request.user.is_creator


class HasVerifiedEmail(BasePermission):
    """
    Allows access only to creator users.
    """

    message = "Only creators are allowed to perform this action."
    code = "creator_required"

    def has_permission(self, request, view):
        return request.user.email_verified
