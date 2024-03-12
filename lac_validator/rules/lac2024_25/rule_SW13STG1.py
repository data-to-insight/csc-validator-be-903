import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW13STG1",
    message="The reason for social worker change is either not valid or has not been entered.",
    affected_fields=["SW_REASON"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]
        df["index"] = df.index

        collection_start = dfs["metadata"]["collection_start"]

        valid_reasons = [
            "MANAGE",
            "FCONTA",
            "LEFTRL",
            "ORGRST",
            "TSPROC",
            "ABSENC",
            "CHCHAN",
            "PCCHAN",
            "SWDIED",
            "OTHERS",
        ]

        df["SW_DECOM"] = pd.to_datetime(
            df["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        df["SW_DEC"] = pd.to_datetime(df["SW_DEC"], format="%d/%m/%Y", errors="coerce")
        collection_start = pd.to_datetime(collection_start, format="%d/%m/%Y")

        df = df.sort_values(["CHILD", "SW_DECOM"], ascending=True)

        last_of_last = df[df["SW_DECOM"] < collection_start].drop_duplicates(
            "CHILD", keep="last"
        )

        last_of_last_closed = last_of_last[
            (last_of_last["SW_DEC"].isna())
            | (last_of_last["SW_DEC"] >= collection_start)
        ]

        first_of_this = df[df["SW_DECOM"] >= collection_start].drop_duplicates(
            "CHILD", keep="first"
        )

        joined_df = pd.concat([last_of_last_closed, first_of_this], axis=0)

        joined_df = joined_df.sort_values(
            ["CHILD", "SW_DECOM"], ascending=True
        ).drop_duplicates("CHILD", keep="first")
        allowed_nans = joined_df[joined_df["SW_REASON"].isna()]["index"].tolist()

        error_rows = df[
            (~df["SW_REASON"].isin(valid_reasons) | df["SW_REASON"].isna())
        ]["index"].tolist()
        error_rows = set(error_rows) - set(allowed_nans)

        return {"SWEpisodes": list(error_rows)}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "SW_DECOM": "01/04/2000",
                "SW_DEC": "02/04/2000",
                "SW_REASON": "OTHERS",
            },  # 0 pass
            {
                "CHILD": "2",
                "SW_DECOM": "01/04/2000",
                "SW_DEC": "02/04/2000",
                "SW_REASON": "OTHERS",
            },  #  1 pass
            {
                "CHILD": "2",
                "SW_DECOM": "03/04/2000",
                "SW_DEC": "04/04/2000",
                "SW_REASON": pd.NA,
            },  # 2 fail
            {
                "CHILD": "3",
                "SW_DECOM": "03/04/1998",
                "SW_DEC": "04/04/2000",
                "SW_REASON": pd.NA,
            },  # 3 pass
            {
                "CHILD": "3",
                "SW_DECOM": "05/04/2000",
                "SW_DEC": "06/04/2000",
                "SW_REASON": pd.NA,
            },  # 4 fail
            {
                "CHILD": "4",
                "SW_DECOM": "05/04/1998",
                "SW_DEC": "31/03/2000",
                "SW_REASON": pd.NA,
            },  # 5 fail
            {
                "CHILD": "4",
                "SW_DECOM": "05/04/2000",
                "SW_DEC": "31/04/2000",
                "SW_REASON": pd.NA,
            },  # 6 pass
        ]
    )

    metadata = {"collection_start": "01/04/2000"}

    fake_dfs = {"SWEpisodes": fake_data, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2, 4, 5]}
