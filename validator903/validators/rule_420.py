from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="420",
        description="LA of placement completed but child is looked after under legal status V3 or V4.",
        affected_fields=["PL_LA"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            df = dfs["Episodes"]
            is_short_term = df["LS"].isin(["V3", "V4"])

            mask = is_short_term & df["PL_LA"].notna()
            return {"Episodes": df.index[mask].tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["C2", "V3", "V4", "V3", "V4", "C2"],
            "PL_LA": [pd.NA, "E03934134", "E059635", pd.NA, pd.NA, "NIR"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Episodes": [1, 2]}
