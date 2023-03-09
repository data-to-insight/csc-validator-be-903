from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="566",
        description="The date that the child"
        + chr(39)
        + "s episode of being missing or away from placement without authorisation ended has been completed but whether the child was missing or away without authorisation has not been completed.",
        affected_fields=["MISSING", "MIS_END"],
    )

    def _validate(dfs):
        if "Missing" not in dfs:
            return {}
        else:
            mis = dfs["Missing"]
            error_mask = mis["MISSING"].isna() & mis["MIS_END"].notna()
            return {"Missing": mis.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"MISSING": "M", "MIS_END": pd.NA},  # 0
            {"MISSING": pd.NA, "MIS_END": "07/02/2020"},  # 1  Fails
            {"MISSING": "A", "MIS_END": "03/02/2020"},  # 2
            {"MISSING": pd.NA, "MIS_END": pd.NA},  # 3
            {"MISSING": "M", "MIS_END": "01/02/2020"},  # 4
            {"MISSING": pd.NA, "MIS_END": "13/02/2020"},  # 5  Fails
        ]
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Missing": [1, 5]}
