# Copyright 2026 Mehmet Rahmi Karatay
#
# Licensed under the Creative Commons Attribution 4.0 International License (CC-BY-4.0).
# You may obtain a copy of the License at https://creativecommons.org/licenses/by/4.0/

import csv
import glob
import os
import shutil
import sqlite3
import tempfile
import urllib.request
import zipfile

from config_loader import LOCAL_NAMES_PATH, RESOURCES_DIR, BoundariesLoader
from geo_math import Point
from query_region import RegionFinder

# Default paths relative to resource directory
existing_dobih = glob.glob(os.path.join(RESOURCES_DIR, "DoBIH*.csv"))
DEFAULT_DOBIH_PATH = (
    existing_dobih[0]
    if existing_dobih
    else os.path.join(RESOURCES_DIR, "DoBIH_v18_4.csv")
)
DEFAULT_LOCAL_NAMES_PATH = LOCAL_NAMES_PATH
DOBIH_DOWNLOAD_URL = "https://www.hill-bagging.co.uk/dobih-downloads/hillcsv.zip"


class HillsDatabaseBuilder:
    """Builder class to compile and populate the SQLite database for UK hills."""

    def __init__(
        self,
        db_path: str,
        dobih_csv_path: str | None = None,
        local_names_csv_path: str | None = None,
    ):
        """Initializes the database builder.

        Args:
            db_path: Path to the target SQLite database file.
            dobih_csv_path: Custom path to DoBIH CSV file.
            local_names_csv_path: Custom path to local names CSV file.
        """
        self.db_path = db_path
        self.dobih_csv_path = dobih_csv_path or DEFAULT_DOBIH_PATH
        self.local_names_csv_path = local_names_csv_path or DEFAULT_LOCAL_NAMES_PATH

    def create_tables(self) -> None:
        """Creates the database schema, tables, and indexes."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Drop tables first to ensure clean schema rebuild
        cursor.execute("DROP TABLE IF EXISTS hills")
        cursor.execute("DROP TABLE IF EXISTS local_names")

        # Create hills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hills (
                name TEXT,
                county TEXT,
                country TEXT,
                height REAL,
                latitude REAL,
                longitude REAL,
                mwis_region TEXT
            )
        """)

        # Create local_names table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_names (
                name TEXT,
                mwis_region TEXT
            )
        """)

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_hills_name ON hills(name COLLATE NOCASE)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_local_names_name ON local_names(name COLLATE NOCASE)"
        )

        conn.commit()
        conn.close()

    def _download_and_extract(self) -> None:
        """Downloads the DoBIH ZIP file and extracts the CSV source."""
        # Create resources directory if it doesn't exist
        os.makedirs(os.path.dirname(self.dobih_csv_path), exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_temp_path = os.path.join(temp_dir, "hillcsv.zip")

            # Download zip file over HTTPS
            req = urllib.request.Request(
                DOBIH_DOWNLOAD_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            with (
                urllib.request.urlopen(req, timeout=30) as response,
                open(  # nosemgrep: detect-path-traversal
                    zip_temp_path, "wb"
                ) as out_file,
            ):
                shutil.copyfileobj(response, out_file)

            # Extract and locate the CSV file
            with zipfile.ZipFile(zip_temp_path) as z:
                csv_members = [m for m in z.namelist() if m.lower().endswith(".csv")]
                if not csv_members:
                    raise FileNotFoundError(
                        "No CSV file found in the downloaded ZIP archive."
                    )

                extracted_path = z.extract(csv_members[0], path=temp_dir)

                # Overwrite/move to target path
                if os.path.exists(self.dobih_csv_path):
                    os.remove(self.dobih_csv_path)
                shutil.move(extracted_path, self.dobih_csv_path)

    def _resolve_mwis_region(self, row: dict[str, str], finder: RegionFinder) -> str:
        """Resolves the MWIS region code for a CSV row based on its coordinates.

        Args:
            row: Parsed CSV row dictionary.
            finder: RegionFinder instance with loaded boundaries.

        Returns:
            Resolved region code or 'notMWIS'.
        """
        try:
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            pt = Point(lat, lon)
            regions = finder.get_matching_regions(pt)
            return ",".join(regions) if regions else "notMWIS"
        except (ValueError, KeyError):
            return "notMWIS"

    def populate_data(self) -> None:
        """Parses the source CSV files and populates database tables."""
        downloaded = False

        try:
            # Trigger download if DoBIH CSV is missing
            if not os.path.exists(self.dobih_csv_path):
                self._download_and_extract()
                downloaded = True

            boundaries = BoundariesLoader.load()
            finder = RegionFinder(boundaries)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing data
            cursor.execute("DELETE FROM hills")
            cursor.execute("DELETE FROM local_names")

            # Populate hills table
            if os.path.exists(self.dobih_csv_path):
                hills_to_insert = []
                with open(  # nosemgrep: detect-path-traversal
                    self.dobih_csv_path, encoding="utf-8-sig"
                ) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        mwis_region = self._resolve_mwis_region(row, finder)
                        try:
                            height = float(row["Metres"])
                        except (ValueError, KeyError):
                            height = 0.0
                        try:
                            lat = float(row.get("Latitude", 0.0))
                            lon = float(row.get("Longitude", 0.0))
                        except (ValueError, TypeError):
                            lat = 0.0
                            lon = 0.0
                        hills_to_insert.append(
                            (
                                row.get("Name", ""),
                                row.get("County", ""),
                                row.get("Country", ""),
                                height,
                                lat,
                                lon,
                                mwis_region,
                            )
                        )

                cursor.executemany(
                    "INSERT INTO hills (name, county, country, height, latitude, longitude, mwis_region) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    hills_to_insert,
                )

            # Populate local_names table
            if os.path.exists(self.local_names_csv_path):
                local_names_to_insert = []
                with open(  # nosemgrep: detect-path-traversal
                    self.local_names_csv_path, encoding="utf-8-sig"
                ) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        local_names_to_insert.append(
                            (
                                row.get("Name", ""),
                                row.get("Region_ID", ""),
                            )
                        )

                cursor.executemany(
                    "INSERT INTO local_names (name, mwis_region) VALUES (?, ?)",
                    local_names_to_insert,
                )

            conn.commit()
            conn.close()

        finally:
            # Clean up only if downloaded by this script execution
            if downloaded and os.path.exists(self.dobih_csv_path):
                os.remove(self.dobih_csv_path)


if __name__ == "__main__":
    import argparse

    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_db = os.path.normpath(
        os.path.join(script_dir, "..", "cache", "uk_hills.db")
    )

    parser = argparse.ArgumentParser(
        description="Build SQLite database cache for hills and local names."
    )
    parser.add_argument(
        "--db-path",
        default=default_db,
        help="Path to the target SQLite database file.",
    )
    parser.add_argument(
        "--csv-path",
        default=DEFAULT_DOBIH_PATH,
        help="Path to the source DoBIH CSV database.",
    )

    args = parser.parse_args()

    builder = HillsDatabaseBuilder(
        db_path=args.db_path,
        dobih_csv_path=args.csv_path,
    )
    builder.create_tables()
    builder.populate_data()
