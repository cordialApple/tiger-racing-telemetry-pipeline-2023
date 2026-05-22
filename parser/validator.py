from collections.abc import Iterable
from dataclasses import dataclass, field

from parser.models import SensorSpec


@dataclass
class ValidationReport:
    out_of_range: int = 0
    unknown_sensors: set[str] = field(default_factory=set)


class SensorValidator:
    """Advisory range checking; flags out-of-range values but never rejects them."""

    def __init__(self, specs: list[SensorSpec]):
        self._specs = {spec.name: spec for spec in specs}

    def validate(self, readings: Iterable[tuple]) -> ValidationReport:
        report = ValidationReport()
        for _ts, name, value in readings:
            spec = self._specs.get(name)
            if spec is None:
                report.unknown_sensors.add(name)
                continue
            if spec.min_range is not None and spec.max_range is not None:
                if value < spec.min_range or value > spec.max_range:
                    report.out_of_range += 1
        return report
