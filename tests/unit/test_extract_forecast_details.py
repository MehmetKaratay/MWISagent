# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

from app.agent_logic import load_extract_details


def test_extract_forecast_details_cloud():
    """Verify that cloud category filters only cloud-related fields."""
    extract_fn = load_extract_details()
    mock_data = {
        "WH": {
            "region": "West Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "date": "Sunday 5th July 2026",
                    "last_updated": "Sat 4th Jul 26 at 4:17PM",
                    "uk_summary": "Rain sets in.",
                    "region_headline": "Drizzly tops.",
                    "wind_headline": "Southwesterly 20 to 30mph.",
                    "wind_effect": "Strenuous walking.",
                    "precip_headline": "Rain sets in.",
                    "precip_detail": "Rain sets in persistently.",
                    "cloud_headline": "Becoming extensive.",
                    "cloud_detail": "Bases 700-1000m.",
                    "chance_cloud_free": "30%",
                    "sun_clarity": "Sunshine occasionally.",
                    "temp": "9C.",
                    "freezing_level": "Above summits.",
                    "Dcode": "D0",
                }
            ],
            "outlook": {"Dcode": "Doutlook", "outlook": "Settled weather."},
        }
    }

    filtered = extract_fn(mock_data, ["cloud"])
    day = filtered["WH"]["days"][0]

    # Metadata preserved
    assert day["date"] == "Sunday 5th July 2026"
    assert day["forecast_index"] == 0
    assert day["Dcode"] == "D0"

    # Cloud fields kept
    assert day["uk_summary"] == "Rain sets in."
    assert day["region_headline"] == "Drizzly tops."
    assert day["cloud_headline"] == "Becoming extensive."
    assert day["cloud_detail"] == "Bases 700-1000m."
    assert day["chance_cloud_free"] == "30%"

    # Other fields pruned
    assert "wind_headline" not in day
    assert "precip_detail" not in day
    assert "temp" not in day


def test_extract_forecast_details_default_headlines():
    """Verify that empty category defaults to headline-only fields."""
    extract_fn = load_extract_details()
    mock_data = {
        "WH": {
            "region": "West Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "date": "Sunday 5th July 2026",
                    "last_updated": "Sat 4th Jul 26 at 4:17PM",
                    "uk_summary": "Rain sets in.",
                    "region_headline": "Drizzly tops.",
                    "wind_headline": "Southwesterly 20 to 30mph.",
                    "wind_effect": "Strenuous walking.",
                    "precip_headline": "Rain sets in.",
                    "precip_detail": "Rain sets in persistently.",
                    "cloud_headline": "Becoming extensive.",
                    "cloud_detail": "Bases 700-1000m.",
                    "chance_cloud_free": "30%",
                    "sun_clarity": "Sunshine occasionally.",
                    "temp": "9C.",
                    "freezing_level": "Above summits.",
                    "Dcode": "D0",
                }
            ],
            "outlook": {"Dcode": "Doutlook", "outlook": "Settled weather."},
        }
    }

    filtered = extract_fn(mock_data, [])
    day = filtered["WH"]["days"][0]

    assert day["uk_summary"] == "Rain sets in."
    assert day["region_headline"] == "Drizzly tops."
    assert day["wind_headline"] == "Southwesterly 20 to 30mph."
    assert day["precip_headline"] == "Rain sets in."
    assert day["cloud_headline"] == "Becoming extensive."

    assert "wind_effect" not in day
    assert "precip_detail" not in day
    assert "cloud_detail" not in day
    assert "chance_cloud_free" not in day
    assert "temp" not in day

    # Outlook preserved by default for general summaries
    assert "outlook" in filtered["WH"]


def test_extract_forecast_details_full():
    """Verify that 'full' category preserves all fields."""
    extract_fn = load_extract_details()
    mock_data = {
        "WH": {
            "region": "West Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "date": "Sunday 5th July 2026",
                    "last_updated": "Sat 4th Jul 26 at 4:17PM",
                    "uk_summary": "Rain sets in.",
                    "region_headline": "Drizzly tops.",
                    "wind_headline": "Southwesterly 20 to 30mph.",
                    "wind_effect": "Strenuous walking.",
                    "precip_headline": "Rain sets in.",
                    "precip_detail": "Rain sets in persistently.",
                    "cloud_headline": "Becoming extensive.",
                    "cloud_detail": "Bases 700-1000m.",
                    "chance_cloud_free": "30%",
                    "sun_clarity": "Sunshine occasionally.",
                    "temp": "9C.",
                    "freezing_level": "Above summits.",
                    "Dcode": "D0",
                }
            ],
            "outlook": {"Dcode": "Doutlook", "outlook": "Settled weather."},
        }
    }

    filtered = extract_fn(mock_data, ["full"])
    assert filtered == mock_data


def test_extract_forecast_details_ordering():
    """Verify that the keys in day forecast dictionaries are deterministically sorted."""
    extract_fn = load_extract_details()
    mock_data = {
        "WH": {
            "region": "West Highlands",
            "days": [
                {
                    "forecast_index": 0,
                    "date": "Sunday 5th July 2026",
                    "last_updated": "Sat 4th Jul 26 at 4:17PM",
                    "uk_summary": "Rain sets in.",
                    "region_headline": "Drizzly tops.",
                    "wind_headline": "Southwesterly 20 to 30mph.",
                    "wind_effect": "Strenuous walking.",
                    "precip_headline": "Rain sets in.",
                    "precip_detail": "Rain sets in persistently.",
                    "cloud_headline": "Becoming extensive.",
                    "cloud_detail": "Bases 700-1000m.",
                    "chance_cloud_free": "30%",
                    "sun_clarity": "Sunshine occasionally.",
                    "temp": "9C.",
                    "freezing_level": "Above summits.",
                    "Dcode": "D0",
                }
            ],
            "outlook": {"Dcode": "Doutlook", "outlook": "Settled weather."},
        }
    }

    # Case: User asked for ["cloud"]
    filtered = extract_fn(mock_data, ["cloud"])
    day_keys = list(filtered["WH"]["days"][0].keys())

    # We expect: date, last_updated, cloud_headline, cloud_detail, chance_cloud_free (in mapping order),
    # then uk_summary, region_headline (only if index is 0), then remaining matching *_headline (wind_headline, precip_headline),
    # then other allowed fields (forecast_index, Dcode)
    expected_order = [
        "date",
        "last_updated",
        "cloud_headline",
        "cloud_detail",
        "chance_cloud_free",
        "uk_summary",
        "region_headline",
        "forecast_index",
        "Dcode",
    ]
    assert day_keys == expected_order
