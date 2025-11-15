from rest_framework.permissions import BasePermission

from .models import User


class IsOperatorOrAdmin(BasePermission):
    """
    Доступ только для операторов и администраторов CRM.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {User.Role.ADMIN, User.Role.OPERATOR}
        )

