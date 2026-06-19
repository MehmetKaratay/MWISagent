import unittest
import os
import tempfile
from get_forecast_url import get_forecast_url

class TestGetForecastUrl(unittest.TestCase):
    def setUp(self):
        # Create a temporary CSV file mimicking the structure of mwis-regions.csv for tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "test-regions.csv")
        with open(self.csv_path, "w") as f:
            f.write("RegionCode,RegionName,Country,Url\n")
            f.write("NW,North West Highlands,Scotland,https://mwis.org.uk/forecasts/scottish/the-northwest-highlands/text\n")
            f.write("WH,West Highlands,Scotland,https://mwis.org.uk/forecasts/scottish/west-highlands/text\n")
            f.write("EH,Eastern Highlands,Scotland,https://mwis.org.uk/forecasts/scottish/cairngorms/text\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_url_by_exact_region_code(self):
        url = get_forecast_url("WH", self.csv_path)
        self.assertEqual(url, "https://mwis.org.uk/forecasts/scottish/west-highlands/text")

    def test_get_url_by_lowercase_region_code(self):
        url = get_forecast_url("wh", self.csv_path)
        self.assertEqual(url, "https://mwis.org.uk/forecasts/scottish/west-highlands/text")

    def test_get_url_by_exact_region_name(self):
        url = get_forecast_url("North West Highlands", self.csv_path)
        self.assertEqual(url, "https://mwis.org.uk/forecasts/scottish/the-northwest-highlands/text")

    def test_get_url_by_lowercase_region_name(self):
        url = get_forecast_url("north west highlands", self.csv_path)
        self.assertEqual(url, "https://mwis.org.uk/forecasts/scottish/the-northwest-highlands/text")

    def test_get_url_with_surrounding_whitespace(self):
        url = get_forecast_url("  EH  ", self.csv_path)
        self.assertEqual(url, "https://mwis.org.uk/forecasts/scottish/cairngorms/text")

    def test_get_url_invalid_query_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_forecast_url("Invalid Region", self.csv_path)

    def test_get_url_empty_query_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_forecast_url("", self.csv_path)

if __name__ == "__main__":
    unittest.main()
