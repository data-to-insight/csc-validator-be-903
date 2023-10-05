import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="565",
    message="The date that the child started to be missing or away from placement without authorisation has been completed but whether the child was missing or away from placement without authorisation has not been completed.",
    affected_fields=["MISSING", "MIS_START"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}
    else:
        missing = dfs["Missing"]
        mask = missing["MIS_START"].notna() & missing["MISSING"].isna()
        error_locations = missing.index[mask]
        return {"Missing": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"MISSING": "M", "MIS_START": pd.NA},  # 0
            {"MISSING": pd.NA, "MIS_START": "07/02/2020"},  # 1
            {"MISSING": "A", "MIS_START": "03/02/2020"},  # 2
            {"MISSING": pd.NA, "MIS_START": pd.NA},  # 3
            {"MISSING": "M", "MIS_START": pd.NA},  # 4
            {"MISSING": "A", "MIS_START": "13/02/2020"},  # 5
        ]
    )

    fake_dfs = {"Missing": fake_data}

    assert validate(fake_dfs) == {"Missing": [1]}
