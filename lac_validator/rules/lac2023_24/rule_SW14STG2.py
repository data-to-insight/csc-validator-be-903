import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW14STG2",
    message="Social worker episode date ceased is blank.",
    affected_fields=["SW_DEC"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        df["SW_DEC"] = pd.to_datetime(df["SW_DEC"], format="%d/%m/%Y", errors="coerce")
        df["SW_DECOM"] = pd.to_datetime(
            df["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        df["index"] = df.index

        empty_dec = df[df["SW_DEC"].isna()]

        df = df.sort_values(["CHILD", "SW_DECOM"])
        latest_episode = df.drop_duplicates("CHILD", keep="last")

        error_rows = empty_dec[~empty_dec["index"].isin(latest_episode["index"])][
            "index"
        ]

        return {"SWEpisodes": error_rows.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "1", "SW_DECOM": "01/01/2000", "SW_DEC": "01/01/2000"},
            {"CHILD": "1", "SW_DECOM": "02/01/2000", "SW_DEC": pd.NA},
            {"CHILD": "2", "SW_DECOM": "01/01/2000", "SW_DEC": pd.NA},
            {"CHILD": "2", "SW_DECOM": "02/01/2000", "SW_DEC": pd.NA},
            {"CHILD": "3", "SW_DECOM": "01/01/2000", "SW_DEC": pd.NA},
        ]
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2]}
