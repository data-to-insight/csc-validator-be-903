from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="179",
        description="Placement location code is not a valid code.",
        affected_fields=["PL_LOCATION"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            df = dfs["Episodes"]
            is_short_term = df["LS"].isin(["V3", "V4"])

            # Because PL_LOCATION is derived, it will always be valid if present
            mask = ~is_short_term & df["PL_LOCATION"].isna()
            return {"Episodes": df.index[mask].tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["C2", "C2", "C2", "V3", "V4"],
            "PL_LOCATION": [
                "IN",
                "OUT",
                pd.NA,
                pd.NA,
                pd.NA,
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Episodes": [2]}
