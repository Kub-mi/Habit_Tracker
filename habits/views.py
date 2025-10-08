from rest_framework import viewsets, permissions, decorators
from rest_framework.response import Response
from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPagination

class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all().order_by("-created_at")
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HabitPagination  # ← вот это важно

    def get_queryset(self):
        # свои привычки
        return Habit.objects.filter(user=self.request.user).order_by("-created_at")

    @decorators.action(detail=False, methods=["get"], url_path="public", permission_classes=[permissions.AllowAny])
    def public(self, request):
        qs = Habit.objects.filter(is_public=True).order_by("-created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)