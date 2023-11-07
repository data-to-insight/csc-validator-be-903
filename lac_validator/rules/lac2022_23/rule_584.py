import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="584",
    message="If the date of the decision that the child should be placed for adoption in the current year is different to the date of the decision recorded in a previous year, then the decision to place the child for adoption must have changed, either in the current year or the previous year and the date should not be before the date of the earlier decision to place the child for adoption.",
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
        pa_last = dfs["PlacedAdoption_last"]

        df = df[
            (df["DATE_PLACED_CEASED"].notna()) | (df["REASON_PLACED_CEASED"].notna())
        ]
        df_merged = df.merge(
            pa_last, how="left", on="CHILD", suffixes=("_current", "_last")
        )
        df_merged = df_merged[df_merged["DATE_PLACED_last"].notna()]

        error_mask = df_merged["DATE_PLACED_current"] < df_merged["DATE_PLACED_last"]
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
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": pd.NA,
            },  # 4 pass
            {
                "CHILD": "child5",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "01/02/2021",
                "REASON_PLACED_CEASED": "XX",
            },  # 5 pass, test DP_last null
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
                "DATE_PLACED_CEASED": "01/02/2020",
                "REASON_PLACED_CEASED": "xx",
            },  # 4
            {
                "CHILD": "child6",
                "DATE_PLACED": pd.NA,
                "DATE_PLACED_CEASED": "01/02/2020",
                "REASON_PLACED_CEASED": "xx",
            },  # 5
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

    assert validate(fake_dfs) == {"PlacedAdoption": [0, 1, 2]}
