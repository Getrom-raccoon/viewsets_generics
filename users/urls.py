from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, ProfileView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', ProfileView.as_view(), name='profile'),
]