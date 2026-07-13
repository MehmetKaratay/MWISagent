# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

import importlib.util
import os


def _load_resolve_shift():
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "app",
        "skills",
        "mwis-website",
        "identify_outing_date",
        "scripts",
        "resolve_shift.py",
    )
    spec = importlib.util.spec_from_file_location("resolve_shift", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.resolve_shift


resolve_shift = _load_resolve_shift()


def test_resolve_shift_forward():
    assert resolve_shift("D0", "next day") == "D1"
    assert resolve_shift("D1", "following day") == "D2"
    assert resolve_shift("D2", "day after") == "D3"
    assert resolve_shift("D3", "tomorrow") == "D3"


def test_resolve_shift_backward():
    assert resolve_shift("D3", "previous day") == "D2"
    assert resolve_shift("D2", "day before") == "D1"
    assert resolve_shift("D1", "yesterday") == "D0"
    assert resolve_shift("D0", "previous day") == "D0"


def test_resolve_shift_invalid():
    assert resolve_shift("Doutlook", "next day") == "D0"
    assert resolve_shift("invalid", "next day") == "D0"
