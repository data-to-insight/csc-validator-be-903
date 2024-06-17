import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW13STG1",
    message="The reason for social worker change is either not valid or has not been entered.",
    affected_fields=["SW_REASON"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]
        df["index"] = df.index

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

        df.sort_values(["CHILD", "SW_DECOM", "SW_DEC"], ascending=True, inplace=True)

        index_of_first = df.drop_duplicates("CHILD", keep="first")

        allowed_nans = index_of_first[index_of_first["SW_REASON"].isna()][
            "index"
        ].tolist()

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
            },  # 5 pass - first in report data
            {
                "CHILD": "4",
                "SW_DECOM": "05/04/2000",
                "SW_DEC": "31/04/2000",
                "SW_REASON": pd.NA,
            },  # 6 fail second in report data
        ]
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2, 4, 6]}
