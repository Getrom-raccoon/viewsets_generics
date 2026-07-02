from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserRegistrationView, PaymentViewSet, ProfileView, CreatePaymentView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
]