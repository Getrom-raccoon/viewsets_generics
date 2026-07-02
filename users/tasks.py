from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Payment
from lms.models import Subscription

User = get_user_model()


@shared_task
def send_course_update_email(course_id, user_id, course_title):
    """Отправка письма пользователю об обновлении курса"""
    user = User.objects.get(id=user_id)
    subject = f'Обновление курса "{course_title}"'
    message = f'Здравствуйте, {user.email}!\n\nКурс "{course_title}" был обновлён. Зайдите и посмотрите новые материалы.\n\nС уважением, команда LMS.'
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@shared_task
def notify_subscribers_about_course_update(course_id):
    """Отправка уведомлений всем подписчикам курса"""
    from lms.models import Course
    course = Course.objects.get(id=course_id)
    subscriptions = Subscription.objects.filter(course=course).select_related('user')
    for subscription in subscriptions:
        send_course_update_email.delay(course_id, subscription.user.id, course.title)


@shared_task
def block_inactive_users():
    """Блокировка пользователей, не заходивших более месяца"""
    month_ago = timezone.now() - timedelta(days=30)
    users = User.objects.filter(last_login__lt=month_ago, is_active=True)
    count = users.update(is_active=False)
    return f'Заблокировано {count} неактивных пользователей'