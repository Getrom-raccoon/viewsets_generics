from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner, IsModeratorOrOwner, IsOwnerOrReadOnly


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов с разграничением прав"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            # Список и просмотр доступны всем (авторизованным)
            self.permission_classes = [IsAuthenticated]
        elif self.action in ('create',):
            # Создание только для обычных пользователей (не модераторов)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ('update', 'partial_update'):
            # Редактирование: модератор или владелец
            self.permission_classes = [IsAuthenticated, IsModeratorOrOwner]
        elif self.action in ('destroy',):
            # Удаление: только владелец (модератор не может удалять)
            self.permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        # Автоматическая привязка владельца
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """ViewSet для уроков с разграничением прав"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = [IsAuthenticated]
        elif self.action in ('create',):
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ('update', 'partial_update'):
            self.permission_classes = [IsAuthenticated, IsModeratorOrOwner]
        elif self.action in ('destroy',):
            self.permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)