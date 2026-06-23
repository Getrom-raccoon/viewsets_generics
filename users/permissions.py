from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверка, является ли пользователь модератором"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwner(BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsModeratorOrOwner(BasePermission):
    """Проверка: модератор ИЛИ владелец"""
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Модераторы').exists():
            return True
        return obj.owner == request.user


class IsOwnerOrReadOnly(BasePermission):
    """Только владелец может изменять, остальные только читают"""
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.owner == request.user