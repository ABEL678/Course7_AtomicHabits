import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.services import create_periodic_task
from users.models import User
from django.urls import reverse


class HabitTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            password='test'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            password='moderator',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        self.habit = Habit.objects.create(
            owner=self.user,
            place='На работе',
            time=datetime.time(minute=10),
            action='Написать код',
            is_pleasant=True,
            frequency=1,
            duration=10,
            is_public=True
        )
        self.habit.task = create_periodic_task(
            self.habit.frequency,
            self.habit.pk,
            self.habit.time
        )
        self.habit.save()

    def test_create_habit(self):
        url = reverse('habits:habit_create')
        data = {
            'place': 'На улице',
            'time': '07:50:00',
            'action': 'Погулять с собакой',
            'is_pleasant': False,
            'frequency': 3,
            'duration': 30
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
        data_error = data
        data_error['duration'] = 130
        response = self.client.post(url, data_error, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_habits(self):
        url = reverse('habits:habits_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_list_habits_public(self):
        url = reverse('habits:habits_public_list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_retrieve_habit(self):
        url = reverse('habits:habit_detail', args=[self.habit.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['place'], 'На улице')

    def test_update_habit(self):
        url = reverse('habits:habit_update', args=[self.habit.id])
        data = {'place': 'На работе'}
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['place'], 'На работе')

    def test_destroy_habit(self):
        url = reverse('habits:habit_delete', args=[self.habit.id])
        self.client.force_authenticate(user=self.user)
        print(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)
