# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""Pruning raw forecast JSON payloads to match only requested date codes."""


def filter_forecast_payload(forecasts: dict, resolved: list[str]) -> dict:
    """Filters forecast payload to keep only matching Dcodes and outlook.

    Args:
        forecasts (dict): The complete forecasts dictionary.
        resolved (list[str]): List of resolved day/outlook codes.

    Returns:
        dict: The filtered forecasts dictionary.
    """
    if not resolved:
        return forecasts
    filtered = {}
    for region, f_data in forecasts.items():
        if not isinstance(f_data, dict):
            filtered[region] = f_data
            continue
        f_copy = {k: v for k, v in f_data.items() if k not in ["days", "outlook"]}
        if "days" in f_data:
            f_copy["days"] = [d for d in f_data["days"] if d.get("Dcode") in resolved]
        if "outlook" in f_data and "Doutlook" in resolved:
            f_copy["outlook"] = f_data["outlook"]
        filtered[region] = f_copy
    return filtered
