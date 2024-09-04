# permissions.py

from rest_framework.permissions import BasePermission
from .models import Professional

class IsProfessionalUser(BasePermission):
    """
    Custom permission to only allow access to Professional users.
    """
    def has_permission(self, request, view):
        # Ensure that the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        return Professional.objects.filter(admin=request.user).exists()  # Use 'admin' instead of 'user'
