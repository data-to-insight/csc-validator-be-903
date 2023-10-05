import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="169",
    message="Local Authority (LA) of placement is not valid or is missing. Please check a valid postcode has been entered.",
    affected_fields=["PL_LA"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        is_short_term = df["LS"].isin(["V3", "V4"])

        # Because PL_LA is derived, it will always be valid if present
        mask = ~is_short_term & df["PL_LA"].isna()
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["C2", "C2", "C2", "V3", "V4"],
            "PL_LA": [
                "NIR",
                "E03934134",
                pd.NA,
                pd.NA,
                pd.NA,
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    assert validate(fake_dfs) == {"Episodes": [2]}
