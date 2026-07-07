# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for the caching layer."""

import os
import tempfile
import unittest
from unittest.mock import patch

from app.cache import get_forecast


class TestCacheIntegration(unittest.TestCase):
    """Test suite for cache integration with SQLite."""

    def setUp(self):
        """Docstring for setUp."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_forecasts.db")
        # Ensure we run in development environment to load mocks
        os.environ["MWIS_ENV"] = "development"

    def tearDown(self):
        """Docstring for tearDown."""
        self.temp_dir.cleanup()

    @patch("check_forecast.is_time_in_schedule")
    @patch("check_forecast._is_new_forecast_available")
    def test_get_forecast_miss_populates_cache(self, mock_new_avail, mock_schedule):
        """Verify a cache miss triggers database population from mocks."""
        mock_schedule.return_value = True
        mock_new_avail.return_value = (True, {})

        forecast = get_forecast("NW", db_path=self.db_path)
        self.assertIsNotNone(forecast)
        self.assertEqual(forecast.get("region"), "The Northwest Highlands")

        # Second call should be a hit (using populated database)
        cached_forecast = get_forecast("NW", db_path=self.db_path)
        self.assertEqual(cached_forecast, forecast)
