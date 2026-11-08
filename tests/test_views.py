from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from restaurant.models import Booking, Menu
from restaurant.serializers import MenuSerializer


class HomePageTests(TestCase):
    def test_home_page_serves_html_and_static_css(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'restaurant/index.html')
        self.assertContains(response, 'restaurant/css/style.css')


class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='S3cure-pass-42')
        self.token = Token.objects.create(user=self.user)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')


class MenuApiTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.pasta = Menu.objects.create(title='Pasta', price=Decimal('18.50'), inventory=20)
        self.salad = Menu.objects.create(title='Greek Salad', price=Decimal('12.99'), inventory=25)
        self.list_url = reverse('menu-list')
        self.detail_url = reverse('menu-detail', args=[self.pasta.pk])
        self.payload = {'title': 'Bruschetta', 'price': '7.99', 'inventory': 30}

    def test_list_is_public(self):
        response = self.client.get(self.list_url)
        expected = MenuSerializer(Menu.objects.all(), many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def test_retrieve_is_public(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Pasta')

    def test_create_requires_token(self):
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Menu.objects.count(), 2)

    def test_create(self):
        self.authenticate()
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Menu.objects.filter(title='Bruschetta').exists())

    def test_create_rejects_negative_price(self):
        self.authenticate()
        response = self.client.post(
            self.list_url, {**self.payload, 'price': '-1.00'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        self.authenticate()
        response = self.client.put(self.detail_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pasta.refresh_from_db()
        self.assertEqual(self.pasta.title, 'Bruschetta')
        self.assertEqual(self.pasta.price, Decimal('7.99'))

    def test_delete_requires_token(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Menu.objects.filter(pk=self.pasta.pk).exists())

    def test_delete(self):
        self.authenticate()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Menu.objects.filter(pk=self.pasta.pk).exists())

    def test_missing_item_returns_404(self):
        response = self.client.get(reverse('menu-detail', args=[999999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookingApiTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            name='Adrian',
            no_of_guests=4,
            booking_date=datetime(2030, 1, 15, 19, 0, tzinfo=timezone.utc),
        )
        self.list_url = reverse('booking-list')
        self.detail_url = reverse('booking-detail', args=[self.booking.pk])
        self.payload = {
            'name': 'Mario',
            'no_of_guests': 2,
            'booking_date': '2030-02-01T18:30:00Z',
        }

    def test_list_requires_token(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        self.authenticate()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Adrian')

    def test_create(self):
        self.authenticate()
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Booking.objects.filter(name='Mario', no_of_guests=2).exists())

    def test_create_rejects_zero_guests(self):
        self.authenticate()
        response = self.client.post(
            self.list_url, {**self.payload, 'no_of_guests': 0}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        self.authenticate()
        response = self.client.put(self.detail_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.name, 'Mario')

    def test_delete(self):
        self.authenticate()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Booking.objects.filter(pk=self.booking.pk).exists())


class RegistrationAndLoginTests(APITestCase):
    credentials = {'username': 'newdiner', 'password': 'S3cure-pass-42'}

    def register(self):
        return self.client.post(
            '/auth/users/', {**self.credentials, 'email': 'diner@example.com'}, format='json'
        )

    def test_register_login_and_reach_protected_endpoint(self):
        self.assertEqual(self.register().status_code, status.HTTP_201_CREATED)

        login = self.client.post('/auth/token/login/', self.credentials, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['auth_token']}")
        response = self.client.get(reverse('booking-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_password_fails(self):
        self.register()
        response = self.client.post(
            '/auth/token/login/',
            {'username': 'newdiner', 'password': 'wrong-password'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
