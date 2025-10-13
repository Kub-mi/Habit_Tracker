from rest_framework import decorators, permissions, viewsets

from .models import Habit
from .pagination import HabitPagination
from .permissions import IsAuthenticatedOrReadOnlyPublic, IsOwner
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD: только свои привычки.
    Публичный список: /api/v1/habits/public/ — доступен всем (read-only).
    Пагинация: 5 на страницу.
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticatedOrReadOnlyPublic]

    def get_queryset(self):
        # отдаём только свои привычки; чужие не видны (404 при прямом id)
        return Habit.objects.filter(
            user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        # публичный список — любой может читать
        if self.action == "public":
            return [permissions.AllowAny()]
        # list / create / retrieve — авторизованные
        if self.action in ("list", "create", "retrieve"):
            return [permissions.IsAuthenticated()]
        # update / partial_update / destroy — только владелец
        return [permissions.IsAuthenticated(), IsOwner()]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    @decorators.action(
        detail=False,
        methods=["get"],
        url_path="public",
        permission_classes=[permissions.AllowAny],
    )
    def public(self, request):
        qs = Habit.objects.filter(is_public=True).order_by("-created_at")
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        return self.get_paginated_response(ser.data)
