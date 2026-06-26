from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonTests(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create_user(email='user@test.com', password='password')
        self.moderator = User.objects.create_user(email='moder@test.com', password='password')
        moderator_group, _ = Group.objects.get_or_create(name='Модераторы')
        self.moderator.groups.add(moderator_group)
        self.other_user = User.objects.create_user(email='other@test.com', password='password')

        # Создаем курс
        self.course = Course.objects.create(title='Test Course', owner=self.user)

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            video_url='https://www.youtube.com/watch?v=123',
            course=self.course,
            owner=self.user
        )

        self.client.force_authenticate(user=self.user)

    def test_create_lesson_valid_url(self):
        """Создание урока с корректной ссылкой youtube"""
        url = reverse('lesson-list')
        data = {
            'title': 'New Lesson',
            'description': 'Desc',
            'video_url': 'https://www.youtube.com/watch?v=abc',
            'course': self.course.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_invalid_url(self):
        """Создание урока с некорректной ссылкой (не youtube)"""
        url = reverse('lesson-list')
        data = {
            'title': 'Invalid Lesson',
            'description': 'Desc',
            'video_url': 'https://rutube.ru/video/123',
            'course': self.course.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', response.data)

    def test_update_lesson_owner(self):
        """Обновление урока владельцем"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Title')

    def test_update_lesson_not_owner(self):
        """Обновление урока чужим пользователем (должен быть доступ запрещен)"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Hacked Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_owner(self):
        """Удаление урока владельцем"""
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_not_owner(self):
        """Удаление урока чужим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='password')
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_subscribe(self):
        """Подписка на курс"""
        url = reverse('subscribe')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe(self):
        """Отписка от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse('subscribe')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_unauthorized(self):
        """Неавторизованный пользователь не может подписаться"""
        self.client.force_authenticate(user=None)
        url = reverse('subscribe')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)