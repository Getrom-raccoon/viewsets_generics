from django.core.management.base import BaseCommand
from users.models import Payment
from lms.models import Course, Lesson
from users.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Создает тестовые платежи'

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(email='test@example.com', defaults={'phone': '123'})
        course1, _ = Course.objects.get_or_create(title='Django Course')
        lesson1, _ = Lesson.objects.get_or_create(title='Lesson 1', course=course1)
        lesson2, _ = Lesson.objects.get_or_create(title='Lesson 2', course=course1)

        Payment.objects.create(
            user=user,
            course=course1,
            amount=Decimal('100.00'),
            payment_method='transfer'
        )
        Payment.objects.create(
            user=user,
            lesson=lesson1,
            amount=Decimal('50.00'),
            payment_method='cash'
        )
        Payment.objects.create(
            user=user,
            lesson=lesson2,
            amount=Decimal('30.00'),
            payment_method='transfer'
        )
        self.stdout.write(self.style.SUCCESS('Создано 3 платежа'))