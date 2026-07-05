#!/usr/bin/env /usr/bin/python3
import json
import os
import subprocess
import sys
import unittest

# Paths to the script under test
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "query_region.py")
PYTHON_EXE = sys.executable

SNOWDON_COORDS = ["53.0685", "-4.0763"]
PD_YD_OVERLAP_COORDS = ["53.95", "-2.57"]
PARIS_COORDS = ["48.8566", "2.3522"]
BELFAST_COORDS = ["54.5973", "-5.9301"]
CARLISLE_COORDS = ["54.8924", "-2.9329"]
SHEFFIELD_COORDS = ["53.3811", "-1.4701"]
LONDON_COORDS = ["51.5074", "-0.1278"]


class TestQueryRegionCLI(unittest.TestCase):
    def run_query(self, args):
        cmd = [PYTHON_EXE, SCRIPT_PATH, *args]
        # Run with timeout to prevent hang
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return res

    def test_coordinate_inside_snowdonia(self):
        # Snowdon coords (inside SD)
        res = self.run_query(SNOWDON_COORDS)
        self.assertEqual(res.returncode, 0)
        self.assertIn("SD", res.stdout)
        self.assertIn("Snowdonia & North Wales", res.stdout)

    def test_coordinate_inside_overlap(self):
        # Coords in PD/YD overlap area
        res = self.run_query(PD_YD_OVERLAP_COORDS)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(any(x in res.stdout for x in ["PD", "YD"]))
        self.assertIn("Overlap zone detected", res.stdout)

    def test_out_of_scope_paris(self):
        # Paris (out of UK scope)
        res = self.run_query(PARIS_COORDS)
        self.assertEqual(res.returncode, 2)
        self.assertIn("out of scope", res.stdout.lower() + res.stderr.lower())

    def test_out_of_scope_belfast(self):
        # Belfast (Northern Ireland is excluded from scope)
        res = self.run_query(BELFAST_COORDS)
        self.assertEqual(res.returncode, 2)
        self.assertIn("out of scope", res.stdout.lower() + res.stderr.lower())

    def test_munro_name_lookup_ben_nevis(self):
        res = self.run_query(["Ben Nevis"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("WH", res.stdout)

    def test_munro_name_lookup_ben_hope(self):
        res = self.run_query(["Ben Hope"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("NW", res.stdout)

    def test_name_lookup_fallback_keswick(self):
        # Keswick (resolved via Nominatim to LD)
        res = self.run_query(["Keswick"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("LD", res.stdout)

    def test_carlisle_out_of_area(self):
        # Carlisle is outside all regions, near LD, YD, SU
        res = self.run_query(CARLISLE_COORDS)
        self.assertEqual(res.returncode, 0)
        self.assertIn("not in an mwis area", res.stdout.lower())
        self.assertTrue(any(x in res.stdout for x in ["LD", "YD", "SU"]))

    def test_sheffield_inside_peak_district(self):
        # Sheffield is inside PD on the map overlays
        res = self.run_query(SHEFFIELD_COORDS)
        self.assertEqual(res.returncode, 0)
        self.assertIn("PD", res.stdout)

    def test_london_out_of_area(self):
        # London is far south-east, away from all regions
        res = self.run_query(LONDON_COORDS)
        self.assertEqual(res.returncode, 0)
        self.assertIn("not in an mwis area", res.stdout.lower())

    def test_loch_lomond(self):
        # Loch Lomond -> Inside WH under new boundaries
        res = self.run_query(["Loch Lomond"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("WH", res.stdout)

    def test_carlisle(self):
        # Carlisle -> Not in any region. YD is nearest
        import re

        res = self.run_query(["Carlisle"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("not in an mwis area", res.stdout.lower())
        self.assertIn("YD", res.stdout)
        self.assertTrue(
            re.search(r"km away to the (N|NE|E|SE|S|SW|W|NW)", res.stdout),
            "Direction string missing",
        )

    def test_glasgow(self):
        # Glasgow -> not in any region. "WH" and "SU" are nearest. "SH" may be within closeness tolerance
        res = self.run_query(["Glasgow"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("not in an mwis area", res.stdout.lower())
        self.assertIn("SU", res.stdout)

    def test_json_output_success(self):
        res = self.run_query([*SNOWDON_COORDS, "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertTrue(data.get("in_scope"))
        self.assertTrue(data.get("in_area"))
        self.assertIn("SD", data.get("regions", []))

    def test_json_output_out_of_scope(self):
        res = self.run_query([*PARIS_COORDS, "--json"])
        self.assertEqual(res.returncode, 2)
        data = json.loads(res.stdout)
        self.assertFalse(data.get("in_scope"))
        self.assertEqual(data.get("error"), "OUT_OF_SCOPE")

    def test_grid_references_inside_eh(self):
        for gr in ["NJ 009 020", "NJ 00992 02017", "NJ009020", "NJ0099202017"]:
            res = self.run_query([gr])
            self.assertEqual(res.returncode, 0)
            self.assertIn("EH", res.stdout)
            self.assertIn("Eastern Highlands", res.stdout)

    def test_grid_reference_outside_mwis_area(self):
        res = self.run_query(["TL 561 571"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("not in an mwis area", res.stdout.lower())

    def test_programmatic_find_regions_by_location(self):
        """Verify that find_regions_by_location can be imported and executed programmatically."""
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        from query_region import find_regions_by_location

        data = find_regions_by_location(SNOWDON_COORDS)
        self.assertTrue(data.get("in_scope"))
        self.assertTrue(data.get("in_area"))
        self.assertIn("SD", data.get("regions", []))

        data_paris = find_regions_by_location(PARIS_COORDS)
        self.assertFalse(data_paris.get("in_scope"))


if __name__ == "__main__":
    unittest.main()
