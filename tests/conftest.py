import pytest

import config
from parser.aim_parser import AimParser

SESSION_1 = config.RAW_DIR / "1.csv"


@pytest.fixture(scope="session")
def parsed():
    return AimParser().parse(SESSION_1)
