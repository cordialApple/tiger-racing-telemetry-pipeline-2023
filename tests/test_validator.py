from datetime import datetime

from parser.models import SensorSpec
from parser.validator import SensorValidator

TS = datetime(2023, 10, 7, 14, 29)

SPECS = [
    SensorSpec("ECU RPM", "rpm", "rpm", "integer", 0, 14000),
    SensorSpec("ECU Lambda1", "lambda", "lambda", "float", 0.6, 1.3),
]


def test_in_range():
    report = SensorValidator(SPECS).validate([(TS, "ECU RPM", 8000.0)])
    assert report.out_of_range == 0
    assert report.unknown_sensors == set()


def test_out_of_range_counted():
    report = SensorValidator(SPECS).validate([(TS, "ECU RPM", 20000.0)])
    assert report.out_of_range == 1


def test_unknown_sensor_never_out_of_range():
    report = SensorValidator(SPECS).validate([(TS, "Mystery", 99999.0)])
    assert report.out_of_range == 0
    assert report.unknown_sensors == {"Mystery"}
