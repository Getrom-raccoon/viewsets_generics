from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters
from .models import User, Payment
from .serializers import UserSerializer, UserRegistrationSerializer, PaymentSerializer
from .filters import PaymentFilter
from .permissions import IsModerator, IsOwner
from lms.models import Course
from .services import create_payment_for_course


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


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id required'}, status=400)

        course = get_object_or_404(Course, id=course_id)
        success_url = request.data.get('success_url', 'http://localhost:8000/success/')
        cancel_url = request.data.get('cancel_url', 'http://localhost:8000/cancel/')

        try:
            payment = create_payment_for_course(
                user=request.user,
                course=course,
                success_url=success_url,
                cancel_url=cancel_url
            )
            return Response({
                'payment_id': payment.id,
                'payment_url': payment.payment_url,
                'status': payment.status,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)