from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="564",
        description="Child was missing or away from placement without authorisation and the date started is blank.",
        affected_fields=["MISSING", "MIS_START"],
    )

    def _validate(dfs):
        if "Missing" not in dfs:
            return {}
        else:
            mis = dfs["Missing"]
            error_mask = (
                mis["MISSING"].isin(["M", "A", "m", "a"]) & mis["MIS_START"].isna()
            )
            return {"Missing": mis.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"MISSING": "M", "MIS_START": pd.NA},  # 0  Fails
            {"MISSING": "A", "MIS_START": "07/02/2020"},  # 1
            {"MISSING": "A", "MIS_START": "03/02/2020"},  # 2
            {"MISSING": pd.NA, "MIS_START": pd.NA},  # 3
            {"MISSING": "M", "MIS_START": pd.NA},  # 4  Fails
            {"MISSING": "A", "MIS_START": "13/02/2020"},  # 5
        ]
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Missing": [0, 4]}
