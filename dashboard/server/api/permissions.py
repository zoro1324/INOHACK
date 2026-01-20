from rest_framework import permissions


class IsFarmer(permissions.BasePermission):
    """
    Permission class for Farmer role
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'FARMER'
        )


class IsRanger(permissions.BasePermission):
    """
    Permission class for Ranger role
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'RANGER'
        )


class IsAdmin(permissions.BasePermission):
    """
    Permission class for Admin role
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsFarmerOrRanger(permissions.BasePermission):
    """
    Permission class for Farmer or Ranger roles
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['FARMER', 'RANGER']
        )


class IsRangerOrAdmin(permissions.BasePermission):
    """
    Permission class for Ranger or Admin roles
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['RANGER', 'ADMIN']
        )


class IsOwnerOrRanger(permissions.BasePermission):
    """
    Permission to only allow owners of a device or rangers to access it
    """
    def has_object_permission(self, request, view, obj):
        # Rangers can view all devices
        if request.user.role == 'RANGER':
            return True
        
        # Farmers can only access their own devices
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # For images, check device ownership
        if hasattr(obj, 'device'):
            return obj.device.owner == request.user
        
        return False


class IsDeviceOwner(permissions.BasePermission):
    """
    Permission to only allow device owners to modify their devices
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CanVerifyDetection(permissions.BasePermission):
    """
    Only Rangers can verify detections
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['RANGER', 'ADMIN']
        )
