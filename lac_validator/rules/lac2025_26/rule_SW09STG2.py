import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW09STG2",
    message="Social worker episode appears to have lasted for less than 24 hours.",
    affected_fields=["SW_DECOM", "SW_DEC"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        df["SW_DEC_dt"] = pd.to_datetime(df["SW_DEC"], dayfirst=True, errors="coerce")
        df["SW_DECOM_dt"] = pd.to_datetime(
            df["SW_DECOM"], dayfirst=True, errors="coerce"
        )

        # Removing rows without a dec
        has_dec = df[df["SW_DEC"].notna() | df["SW_DECOM"]].copy()

        has_dec["time_delta"] = has_dec["SW_DEC_dt"] - has_dec["SW_DECOM_dt"]
        print(has_dec)

        error_rows = has_dec[has_dec["time_delta"] < pd.Timedelta(days=3)].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "1", "SW_DEC": "01/01/2000", "SW_DECOM": "02/01/2000"},  # fail
            {"CHILD": "1", "SW_DEC": "04/01/2000", "SW_DECOM": "01/01/2000"},
            {"CHILD": "2", "SW_DEC": "03/01/1901", "SW_DECOM": "01/01/1901"},  # fail
            {"CHILD": "2", "SW_DEC": "01/01/1901", "SW_DECOM": pd.NA},
            {"CHILD": "3", "SW_DEC": pd.NA, "SW_DECOM": pd.NA},
        ]
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 2]}
