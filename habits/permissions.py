from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwner(BasePermission):
    """
    Разрешает доступ только владельцу объекта.
    Используем на объектных операциях (retrieve/update/partial_update/destroy).
    """

    def has_object_permission(self, request, view, obj):
        return obj.user_id == getattr(request.user, "id", None)


class IsAuthenticatedOrReadOnlyPublic(BasePermission):
    """
    Для ViewSet в целом:
    - для кастомного экшена 'public' разрешаем только SAFE методы всем;
    - для остальных действий требуем аутентификацию.
    """

    def has_permission(self, request, view):
        if getattr(view, "action", None) == "public":
            return request.method in SAFE_METHODS
        return request.user and request.user.is_authenticated
