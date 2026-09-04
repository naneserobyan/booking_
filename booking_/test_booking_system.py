import os
import unittest
from datetime import date

from booking_system import (
    BookingSystem,
    NotAvailableError,
    PropertyNotFoundError,
)


class TestBookingSystem(unittest.TestCase):

    def setUp(self):

        self.test_file = "test_data.json"

        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        self.system = BookingSystem(
            data_file=self.test_file
        )

        self.system.add_property(
            "p1",
            "Sunny Apartment",
            50,
        )

    def tearDown(self):

        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_property_is_available(self):

        available = self.system.is_available(
            "p1",
            date(2026, 9, 1),
            date(2026, 9, 5),
        )

        self.assertTrue(available)

    def test_booking_makes_dates_unavailable(self):

        self.system.book(
            "p1",
            "Ani",
            date(2026, 9, 1),
            date(2026, 9, 5),
        )

        available = self.system.is_available(
            "p1",
            date(2026, 9, 2),
            date(2026, 9, 3),
        )

        self.assertFalse(available)

    def test_non_overlapping_booking_is_allowed(self):

        self.system.book(
            "p1",
            "Ani",
            date(2026, 9, 1),
            date(2026, 9, 5),
        )

        available = self.system.is_available(
            "p1",
            date(2026, 9, 5),
            date(2026, 9, 8),
        )

        self.assertTrue(available)

    def test_unavailable_property_raises_error(self):

        self.system.book(
            "p1",
            "Ani",
            date(2026, 9, 1),
            date(2026, 9, 5),
        )

        with self.assertRaises(NotAvailableError):

            self.system.book(
                "p1",
                "Ara",
                date(2026, 9, 3),
                date(2026, 9, 6),
            )

    def test_unknown_property_raises_error(self):

        with self.assertRaises(PropertyNotFoundError):

            self.system.is_available(
                "unknown",
                date(2026, 9, 1),
                date(2026, 9, 5),
            )

    def test_price_calculation(self):

        price = self.system.calculate_price(
            "p1",
            date(2026, 9, 1),
            date(2026, 9, 5),
        )

        self.assertEqual(price, 200)


if __name__ == "__main__":
    unittest.main()