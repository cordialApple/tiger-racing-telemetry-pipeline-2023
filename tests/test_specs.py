from parser.specs import SpecLoader


def test_loads_specs():
    specs = SpecLoader().load()
    by_name = {s.name: s for s in specs}

    rpm = by_name["ECU RPM"]
    assert rpm.min_range == 0
    assert rpm.max_range == 14000

    assert any(s.data_type == "boolean" for s in specs)
    assert any(s.min_range is None and s.max_range is None for s in specs)
