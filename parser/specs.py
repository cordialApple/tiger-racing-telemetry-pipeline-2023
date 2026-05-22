from pathlib import Path

import config
from parser.models import SensorSpec


class SpecLoader:
    def __init__(self, path=config.SPECS_PATH):
        self.path = Path(path)

    def load(self) -> list[SensorSpec]:
        specs = []
        for cells in self._table_rows():
            name, description, data_type, unit, min_range, max_range = cells[:6]
            specs.append(SensorSpec(
                name=name,
                description=description,
                unit=unit or None,
                data_type=data_type,
                min_range=self._to_float(min_range),
                max_range=self._to_float(max_range),
            ))
        return specs

    def _table_rows(self) -> list[list[str]]:
        rows = []
        header_seen = False
        for line in self.path.read_text().splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not header_seen:
                header_seen = True
                continue
            if all(set(c) <= {"-", ":"} for c in cells):
                continue
            rows.append(cells)
        return rows

    @staticmethod
    def _to_float(cell: str) -> float | None:
        return float(cell) if cell else None
