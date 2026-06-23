from rest_framework import serializers
from .models import User, Payment
from lms.serializers import CourseSerializer, LessonSerializer


class PaymentSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source='course', read_only=True)
    lesson_detail = LessonSerializer(source='lesson', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'payment_date', 'course', 'lesson', 'course_detail', 'lesson_detail', 'amount', 'payment_method']


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'is_active', 'is_staff', 'payments']
        read_only_fields = ['is_active', 'is_staff', 'payments']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'city', 'avatar', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user