
from rest_framework.response import Response
from rest_framework import viewsets, permissions, decorators
from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPagination
from .permissions import IsOwner, IsAuthenticatedOrReadOnlyPublic

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticatedOrReadOnlyPublic]

    def get_queryset(self):
        """
        По умолчанию — только привычки текущего пользователя.
        Публичный список отдаём в отдельном action-е.
        """
        return Habit.objects.filter(user=self.request.user).order_by("-created_at")

    def get_permissions(self):
        # Для публичного списка — любой может читать (SAFE)
        if self.action == "public":
            return [permissions.AllowAny()]
        # Для list/create/retrieve нужна аутентификация (задано классом по умолчанию)
        if self.action in ("list", "create"):
            return [permissions.IsAuthenticated()]
        if self.action == "retrieve":
            # объектная проверка владельца сработает в get_object()
            return [permissions.IsAuthenticated()]
        # Для update/partial_update/destroy — владелец
        return [permissions.IsAuthenticated(), IsOwner()]

    def get_object(self):
        obj = super().get_object()
        # объектная проверка владельца
        self.check_object_permissions(self.request, obj)
        return obj

    @decorators.action(
        detail=False, methods=["get"], url_path="public", permission_classes=[permissions.AllowAny]
    )
    def public(self, request):
        """
        Публичные привычки доступны всем на чтение, без JWT.
        Пагинация по 5.
        """
        qs = Habit.objects.filter(is_public=True).order_by("-created_at")
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        return self.get_paginated_response(ser.data)
