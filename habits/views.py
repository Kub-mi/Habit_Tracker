from rest_framework import viewsets, permissions
from .models import Habit
from .serializers import HabitSerializer

class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all().order_by("-created_at")
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]