from datetime import datetime, timezone
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from restaurant.models import Booking, Menu


class MenuModelTests(TestCase):
    def test_str(self):
        item = Menu.objects.create(title='IceCream', price=Decimal('80.00'), inventory=100)
        self.assertEqual(str(item), 'IceCream : 80.00')

    def test_negative_price_is_invalid(self):
        item = Menu(title='IceCream', price=Decimal('-1.00'), inventory=100)
        with self.assertRaises(ValidationError):
            item.full_clean()


class BookingModelTests(TestCase):
    def setUp(self):
        self.when = datetime(2030, 1, 15, 19, 0, tzinfo=timezone.utc)

    def test_str(self):
        booking = Booking.objects.create(name='Adrian', no_of_guests=4, booking_date=self.when)
        self.assertEqual(str(booking), 'Adrian : 4 guests')

    def test_zero_guests_is_invalid(self):
        booking = Booking(name='Adrian', no_of_guests=0, booking_date=self.when)
        with self.assertRaises(ValidationError):
            booking.full_clean()
