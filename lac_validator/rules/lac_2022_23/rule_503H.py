import pandas as pd
from lac_validator.rule_engine import rule_definition


def test_validate():
    

    result = validate(fake_dfs__452_453_503G_503H)

    assert result == {"Episodes": [4, 6]}
