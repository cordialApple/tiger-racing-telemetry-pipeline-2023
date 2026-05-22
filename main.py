import argparse

import uvicorn

import config
from db.connection import Database
from db.repository import ReadingRepository
from db.schema_manager import SchemaManager
from loader.pipeline import Pipeline
from parser.aim_parser import AimParser
from parser.specs import SpecLoader
from parser.validator import SensorValidator


def build_pipeline(db):
    specs = SpecLoader().load()
    return Pipeline(
        db, config.RAW_DIR, config.PROCESSED_DIR,
        AimParser(), SensorValidator(specs),
        ReadingRepository(), specs,
    )


def ingest(db):
    sm = SchemaManager(db)
    sm.apply()
    results = build_pipeline(db).run()
    if any(r.status == "loaded" for r in results):
        sm.refresh_views()
    for r in results:
        detail = r.error if r.status == "error" else f"{r.readings} readings, {r.out_of_range} out of range"
        print(f"{r.source_file}: {r.status} ({detail})")


def serve():
    uvicorn.run("dashboard.api:app", host=config.API_HOST, port=config.API_PORT)


def main():
    parser = argparse.ArgumentParser(description="FSAE telemetry pipeline")
    parser.add_argument("command", nargs="?", default="all",
                        choices=["ingest", "serve", "all"])
    args = parser.parse_args()
    if args.command in ("ingest", "all"):
        ingest(Database())
    if args.command in ("serve", "all"):
        serve()


if __name__ == "__main__":
    main()
