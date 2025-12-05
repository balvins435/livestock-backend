from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to owner or admin"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj == request.user


class IsVerified(permissions.BasePermission):
    """User must be verified"""
    
    def has_permission(self, request, view):
        return request.user.is_verified


class IsAdmin(permissions.BasePermission):
    """User must be admin"""
    
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class IsFarmerOrAdmin(permissions.BasePermission):
    """User must be farmer or admin"""
    
    def has_permission(self, request, view):
        return request.user.role in ['farmer', 'admin']


class IsVeterinarianOrAdmin(permissions.BasePermission):
    """User must be veterinarian or admin"""
    
    def has_permission(self, request, view):
        return request.user.role in ['veterinarian', 'admin']