import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SPECS_PATH = ROOT / "docs" / "sensorspecs.md"

API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))

DB_NAME = os.environ.get("PGDATABASE", "telemetry")
DB_USER = os.environ.get("PGUSER", "fsae")
DB_PASSWORD = os.environ.get("PGPASSWORD", "fsae2023")
DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
