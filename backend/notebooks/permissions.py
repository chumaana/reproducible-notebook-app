from rest_framework import permissions


class IsOwnerOrReadOnlyIfPublic(permissions.BasePermission):
    """
    Custom permission:
    - Owner can do anything
    - Authenticated users can read if public
    - Unauthenticated users can read if public
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for public notebooks
        if request.method in permissions.SAFE_METHODS:
            if obj.is_public:
                return True

        # Write permissions only for owner
        return obj.author == request.user
