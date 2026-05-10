from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            hasattr(request.user, "company")
            and request.user.company.role == Company.Role.ADMIN
        )
