import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="179",
    message="Placement location code is not a valid code.",
    affected_fields=["PL_LOCATION"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        is_short_term = df["LS"].isin(["V3", "V4"])

        # Because PL_LOCATION is derived, it will always be valid if present
        mask = ~is_short_term & df["PL_LOCATION"].isna()
        return {"Episodes": df.index[mask].tolist()}


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

    assert validate(fake_dfs) == {"Episodes": [2]}
