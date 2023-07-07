import json
from pathlib import Path

import pandas as pd
import pytest

from lac_validator.report import _create_child_summary


@pytest.fixture(scope="session")
def report_fixtures():
    with open(Path(__file__).parent / "reports/child_summary.json", 'rt') as file:
        return json.load(file)


@pytest.fixture
def single_test_fixture(request, report_fixtures):
    return report_fixtures[request.param]


@pytest.mark.parametrize("single_test_fixture", [
    "test_ok", "test_missing_context", "test_locator_hints"
], indirect=True)
def test_child_summary(single_test_fixture):
    child_report = pd.DataFrame([single_test_fixture['input']])
    df = _create_child_summary(child_report)
    assert df.to_dict(orient='records') == [single_test_fixture['output']]
