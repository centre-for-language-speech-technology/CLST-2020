from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Permission for checking if a user is registered as a foreign key to an object.

    Requires the view to have a owner_key field setup which refers to the Foreign key of the object which the user
    must equal to. Also requires a get_permissions_object() function which returns the permission object.
    """

    def has_permission(self, request, view):
        """Check if a user has permissions."""
        return request.user == getattr(
            view.get_permissions_object(), view.owner_key
        )
