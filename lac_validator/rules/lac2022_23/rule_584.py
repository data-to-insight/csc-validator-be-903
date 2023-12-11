import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="584",
    message="Date of decision that the child should be placed for adoption this year is different from that recorded last year, but the decision to placed the child for adoption changed and the child should no longer be placed for adoption.",
    affected_fields=["DATE_PLACED"],
)
def validate(dfs):
    # If <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED> has been provided and
    # <DATE_PLACED_CEASED> and or <REASON_PLACED_CEASED> is not NULL then <CURRENT_COLLECTION_YEAR>
    # <DATE_PLACED> must be > <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED>

    if "PlacedAdoption" not in dfs or "PlacedAdoption_last" not in dfs:
        return {}
    else:
        # Rule logic: fail rows where date_placed_current is earlier than date _placed_last
        # in instances where there is no _reason_placed_ceased, and where there is a date_placed_last

        df = dfs["PlacedAdoption"]
        df["index"] = df.index
        pa_last = dfs["PlacedAdoption_last"]

        pa_last = pa_last[
            (pa_last["DATE_PLACED_CEASED"].notna())
            | (pa_last["REASON_PLACED_CEASED"].notna())
        ]
        df_merged = df.merge(
            pa_last, how="inner", on="CHILD", suffixes=("_current", "_last")
        )
        dp_earlier_list = list(
            df_merged[
                df_merged["DATE_PLACED_current"] <= df_merged["DATE_PLACED_last"]
            ].index
        )

        na_current_list = list(
            df_merged[df_merged["DATE_PLACED_current"].isna()]["index"]
        )

        error_mask = df["index"].isin(dp_earlier_list) | df["index"].isin(
            na_current_list
        )

        return {"PlacedAdoption": df.index[error_mask].to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "01/02/2020",
                "REASON_PLACED_CEASED": "xx",
            },  # 0 Fail, test neither null
            {
                "CHILD": "child2",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": "xx",
            },  # 1 Fail, test DPC null
            {
                "CHILD": "child3",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "01/02/2020",
                "REASON_PLACED_CEASED": pd.NA,
            },  # 2 Fail, test RPC null
            {
                "CHILD": "child4",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
            },  # 3 Pass
            {
                "CHILD": "child5",
                "DATE_PLACED": "01/02/2021",
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": pd.NA,
            },  # 4 pass
            {
                "CHILD": "child6",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": "XX",
            },  # 5 pass, test DP_last null
            {
                "CHILD": "child7",
                "DATE_PLACED": pd.NA,
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": "XX",
            },  # 6 fail, DP null
        ]
    )

    fake_last = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "DATE_PLACED": "01/02/2021",
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": "xx",
            },  # 0
            {
                "CHILD": "child2",
                "DATE_PLACED": "01/02/2021",
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": "xx",
            },  # 1
            {
                "CHILD": "child3",
                "DATE_PLACED": "01/02/2021",
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": "xx",
            },  # 2
            {
                "CHILD": "child4",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "01/02/2020",
                "REASON_PLACED_CEASED": "xx",
            },  # 3
            {
                "CHILD": "child5",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "02/02/2020",
                "REASON_PLACED_CEASED": "xx",
            },  # 4
            {
                "CHILD": "child6",
                "DATE_PLACED": pd.NA,
                "DATE_PLACED_CEASED": "01/02/2020",
                "REASON_PLACED_CEASED": "xx",
            },  # 5
            {
                "CHILD": "child7",
                "DATE_PLACED": "01/01/2020",
                "DATE_PLACED_CEASED": "01/02/2020",
                "REASON_PLACED_CEASED": "xx",
            },  # 6
        ]
    )

    fake_data["DATE_PLACED"] = pd.to_datetime(
        fake_data["DATE_PLACED"], format="%d/%m/%Y"
    )
    fake_data["DATE_PLACED_CEASED"] = pd.to_datetime(
        fake_data["DATE_PLACED_CEASED"], format="%d/%m/%Y"
    )

    fake_last["DATE_PLACED"] = pd.to_datetime(
        fake_last["DATE_PLACED"], format="%d/%m/%Y"
    )
    fake_last["DATE_PLACED_CEASED"] = pd.to_datetime(
        fake_last["DATE_PLACED_CEASED"], format="%d/%m/%Y"
    )

    fake_dfs = {"PlacedAdoption": fake_data, "PlacedAdoption_last": fake_last}

    assert validate(fake_dfs) == {"PlacedAdoption": [0, 1, 2, 3, 6]}
