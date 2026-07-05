# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Unit tests for the parse_Dcodes.py module."""

import datetime
import unittest
from parse_Dcodes import get_d_code_for_date


class TestParseDCodes(unittest.TestCase):
    """Test suite for validating get_d_code_for_date resolution logic."""

    def setUp(self):
        self.ref_date = datetime.date(2026, 7, 5)  # Sunday

    def test_past_date(self):
        """Verify past dates return Dold."""
        target = datetime.date(2026, 7, 4)
        self.assertEqual(get_d_code_for_date(target, self.ref_date), "Dold")

    def test_today(self):
        """Verify offset 0 returns D0."""
        target = datetime.date(2026, 7, 5)
        self.assertEqual(get_d_code_for_date(target, self.ref_date), "D0")

    def test_tomorrow(self):
        """Verify offset 1 returns D1."""
        target = datetime.date(2026, 7, 6)
        self.assertEqual(get_d_code_for_date(target, self.ref_date), "D1")

    def test_day_after_tomorrow(self):
        """Verify offset 2 returns D2."""
        target = datetime.date(2026, 7, 7)
        self.assertEqual(get_d_code_for_date(target, self.ref_date), "D2")

    def test_three_days_ahead(self):
        """Verify offset 3 returns D3."""
        target = datetime.date(2026, 7, 8)
        self.assertEqual(get_d_code_for_date(target, self.ref_date), "D3")

    def test_outlook_range(self):
        """Verify offsets 4 to 7 return Doutlook."""
        for offset in range(4, 8):
            target = self.ref_date + datetime.timedelta(days=offset)
            self.assertEqual(get_d_code_for_date(target, self.ref_date), "Doutlook")

    def test_extended_future(self):
        """Verify offsets 8+ return Dfuture."""
        target = datetime.date(2026, 7, 13)
        self.assertEqual(get_d_code_for_date(target, self.ref_date), "Dfuture")
