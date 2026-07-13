# Copyright 2026 Mehmet Rahmi Karatay
#
# Licensed under the Creative Commons Attribution 4.0 International License (CC-BY-4.0).
# You may obtain a copy of the License at https://creativecommons.org/licenses/by/4.0/

import csv
import sqlite3
import sys
from pathlib import Path

# Add scripts directory to sys.path dynamically due to hyphen in path
scripts_dir = (
    Path(__file__).resolve().parent.parent.parent
    / "app"
    / "skills"
    / "mwis-website"
    / "identify_forecast_area"
    / "scripts"
)
sys.path.append(str(scripts_dir))

from build_hills_db import HillsDatabaseBuilder  # noqa: E402


def test_database_schema_creation(tmp_path):
    """Verify that the database file, tables, and indexes are created with correct schemas."""
    db_path = tmp_path / "test_uk_hills.db"

    # Instantiate builder with test DB path
    builder = HillsDatabaseBuilder(db_path=str(db_path))
    builder.create_tables()

    # Assert database file exists
    assert db_path.exists()

    # Connect and verify schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check hills table
    cursor.execute("PRAGMA table_info(hills)")
    hills_cols = {row[1]: row[2] for row in cursor.fetchall()}
    assert "name" in hills_cols
    assert "county" in hills_cols
    assert "country" in hills_cols
    assert "height" in hills_cols
    assert "mwis_region" in hills_cols

    # Check local_names table
    cursor.execute("PRAGMA table_info(local_names)")
    local_names_cols = {row[1]: row[2] for row in cursor.fetchall()}
    assert "name" in local_names_cols
    assert "mwis_region" in local_names_cols

    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row[0] for row in cursor.fetchall()]
    assert "idx_hills_name" in indexes
    assert "idx_local_names_name" in indexes

    conn.close()


def test_database_population(tmp_path):
    """Verify that HillsDatabaseBuilder parses CSVs and populates tables with correct regions."""
    db_path = tmp_path / "test_uk_hills.db"
    mock_dobih_csv = tmp_path / "mock_dobih.csv"
    mock_local_names_csv = tmp_path / "mock_local_names.csv"

    # Write mock DoBIH CSV using csv.DictWriter for robustness
    headers = [
        "Number",
        "Name",
        "Parent (SMC)",
        "Parent name (SMC)",
        "Section",
        "Region",
        "Area",
        "Island",
        "Topo Section",
        "County",
        "Classification",
        "Map 1:50k",
        "Map 1:25k",
        "Metres",
        "Feet",
        "Grid ref",
        "Grid ref 10",
        "Drop",
        "Col grid ref",
        "Col height",
        "Feature",
        "Observations",
        "Survey",
        "Climbed",
        "Country",
        "County Top",
        "Revision",
        "Comments",
        "Streetmap/MountainViews",
        "Google Maps",
        "Hill-bagging",
        "Xcoord",
        "Ycoord",
        "Latitude",
        "Longitude",
    ]

    with open(mock_dobih_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        # 1. Ben Nevis (WH region: ~56.7969, -5.0036)
        writer.writerow(
            {
                "Number": "1",
                "Name": "Ben Nevis",
                "County": "Highland",
                "Metres": "1344.5",
                "Country": "S",
                "Latitude": "56.7969",
                "Longitude": "-5.0036",
            }
        )
        # 2. Snowdon (SD region: ~53.0685, -4.0763)
        writer.writerow(
            {
                "Number": "2",
                "Name": "Snowdon",
                "County": "Gwynedd",
                "Metres": "1085.0",
                "Country": "W",
                "Latitude": "53.0685",
                "Longitude": "-4.0763",
            }
        )
        # 3. London Hill (Not in MWIS: ~51.5074, -0.1278)
        writer.writerow(
            {
                "Number": "3",
                "Name": "London Hill",
                "County": "Greater London",
                "Metres": "100.0",
                "Country": "E",
                "Latitude": "51.5074",
                "Longitude": "-0.1278",
            }
        )

    # Write mock local names CSV
    mock_local_names_csv.write_text("Name,Region_ID\nCuillin,NW\nBrecon Beacons,BB\n")

    builder = HillsDatabaseBuilder(
        db_path=str(db_path),
        dobih_csv_path=str(mock_dobih_csv),
        local_names_csv_path=str(mock_local_names_csv),
    )
    builder.create_tables()
    builder.populate_data()

    # Assert values in hills table
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, county, country, height, mwis_region FROM hills ORDER BY height DESC"
    )
    hills = cursor.fetchall()
    assert len(hills) == 3

    # Ben Nevis
    assert hills[0] == ("Ben Nevis", "Highland", "S", 1344.5, "WH")
    # Snowdon
    assert hills[1] == ("Snowdon", "Gwynedd", "W", 1085.0, "SD")
    # London
    assert hills[2] == ("London Hill", "Greater London", "E", 100.0, "notMWIS")

    # Assert values in local_names table
    cursor.execute("SELECT name, mwis_region FROM local_names ORDER BY name")
    local_names = cursor.fetchall()
    assert len(local_names) == 2
    assert local_names[0] == ("Brecon Beacons", "BB")
    assert local_names[1] == ("Cuillin", "NW")

    conn.close()


def test_download_triggered_when_csv_missing(tmp_path, monkeypatch):
    """Verify that download and extraction are triggered if the DoBIH CSV is missing."""
    db_path = tmp_path / "test_uk_hills.db"
    mock_csv_path = tmp_path / "mock_dobih.csv"

    # Ensure CSV does not exist
    if mock_csv_path.exists():
        mock_csv_path.unlink()

    download_called = False

    def mock_download():
        nonlocal download_called
        download_called = True
        # Simulate download extracting the CSV file
        mock_csv_path.write_text(
            "Number,Name,Metres,Country,Latitude,Longitude\n1,Ben Nevis,1344.5,S,56.7969,-5.0036\n"
        )

    builder = HillsDatabaseBuilder(
        db_path=str(db_path),
        dobih_csv_path=str(mock_csv_path),
    )

    monkeypatch.setattr(builder, "_download_and_extract", mock_download)

    builder.create_tables()
    builder.populate_data()

    assert download_called is True
    assert not mock_csv_path.exists()


def test_download_skipped_when_csv_present(tmp_path, monkeypatch):
    """Verify that download and extraction are skipped if the DoBIH CSV is already present."""
    db_path = tmp_path / "test_uk_hills.db"
    mock_csv_path = tmp_path / "mock_dobih.csv"

    # Pre-create the CSV file
    mock_csv_path.write_text(
        "Number,Name,Metres,Country,Latitude,Longitude\n1,Ben Nevis,1344.5,S,56.7969,-5.0036\n"
    )

    download_called = False

    def mock_download():
        nonlocal download_called
        download_called = True

    builder = HillsDatabaseBuilder(
        db_path=str(db_path),
        dobih_csv_path=str(mock_csv_path),
    )

    monkeypatch.setattr(builder, "_download_and_extract", mock_download)

    builder.create_tables()
    builder.populate_data()

    assert download_called is False
    assert mock_csv_path.exists()


def test_cleanup_removes_downloaded_files(tmp_path, monkeypatch):
    """Verify that temporary CSV files downloaded by the script are deleted at the end."""
    db_path = tmp_path / "test_uk_hills.db"
    mock_csv_path = tmp_path / "mock_dobih.csv"

    # Ensure CSV does not exist initially
    if mock_csv_path.exists():
        mock_csv_path.unlink()

    def mock_download():
        mock_csv_path.write_text(
            "Number,Name,Metres,Country,Latitude,Longitude\n1,Ben Nevis,1344.5,S,56.7969,-5.0036\n"
        )

    builder = HillsDatabaseBuilder(
        db_path=str(db_path),
        dobih_csv_path=str(mock_csv_path),
    )

    monkeypatch.setattr(builder, "_download_and_extract", mock_download)

    builder.create_tables()
    builder.populate_data()

    # The dynamically downloaded CSV should have been deleted
    assert not mock_csv_path.exists()


def test_cleanup_preserves_preexisting_files(tmp_path, monkeypatch):
    """Verify that CSV files that existed prior to running the script are not deleted."""
    db_path = tmp_path / "test_uk_hills.db"
    mock_csv_path = tmp_path / "mock_dobih.csv"

    # Pre-create the CSV
    mock_csv_path.write_text(
        "Number,Name,Metres,Country,Latitude,Longitude\n1,Ben Nevis,1344.5,S,56.7969,-5.0036\n"
    )

    download_called = False

    def mock_download():
        nonlocal download_called
        download_called = True

    builder = HillsDatabaseBuilder(
        db_path=str(db_path),
        dobih_csv_path=str(mock_csv_path),
    )

    monkeypatch.setattr(builder, "_download_and_extract", mock_download)

    builder.create_tables()
    builder.populate_data()

    # Download was not called, so CSV was pre-existing and must not be deleted
    assert download_called is False
    assert mock_csv_path.exists()


def test_cli_main_entrypoint(tmp_path, monkeypatch):
    """Verify that build_hills_db.py can be run as a CLI script with arguments."""
    import runpy

    db_path = tmp_path / "cli_test_hills.db"
    mock_csv_path = tmp_path / "cli_test_dobih.csv"

    # Pre-create the CSV file
    mock_csv_path.write_text(
        "Number,Name,Metres,Country,Latitude,Longitude\n1,Ben Nevis,1344.5,S,56.7969,-5.0036\n"
    )

    # Mock sys.argv
    test_args = [
        "build_hills_db.py",
        "--db-path",
        str(db_path),
        "--csv-path",
        str(mock_csv_path),
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    # Run the script's __main__ code
    script_path = scripts_dir / "build_hills_db.py"
    runpy.run_path(str(script_path), run_name="__main__")

    # Verify the database was created and populated
    assert db_path.exists()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name, mwis_region FROM hills")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0] == ("Ben Nevis", "WH")
