from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import User, Payment
from .serializers import UserSerializer, UserRegistrationSerializer, PaymentSerializer
from .filters import PaymentFilter
from .permissions import IsModerator, IsOwner


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей (только для админов/модераторов)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('create', 'list', 'retrieve', 'update', 'partial_update', 'destroy'):
            self.permission_classes = [IsAuthenticated, IsModerator]
        return [permission() for permission in self.permission_classes]


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя (доступно всем)"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр платежей"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


class ProfileView(generics.RetrieveAPIView):
    """Профиль пользователя с историей платежей"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user