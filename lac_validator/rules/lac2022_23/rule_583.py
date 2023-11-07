import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="583",
    message="More than one date the child should be placed for adoption has been reported, but an earlier decision has not been revoked. Check that both dates are required and add in the date the earlier decision was revoked. Note this may be in a previous year.",
    affected_fields=["DATE_PLACED", "DATE_PLACED_CEASED"],
)
def validate(dfs):
    # If more than one <DATE_PLACED> is present, then all but the latest <DATE_PLACED> must have <DATE_PLACED_CEASED>
    # (The latest <DATE_PLACED> may or may not have <DATE_PLACED_CEASED>)
    # Apply for 2023 onwards
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        # If a child has more than one Na in date_placed_cease, they fail, sending all Na rows as errors
        df = dfs["PlacedAdoption"]
        ceased_nans = df[df["DATE_PLACED_CEASED"].isna()]
        nans_count = ceased_nans["CHILD"].value_counts()
        too_many_nans_list = list(nans_count[nans_count > 1].index)
        too_many_nans = ceased_nans[ceased_nans["CHILD"].isin(too_many_nans_list)]
        too_many_nans_index = list(too_many_nans.index)

        # If a child has an earlier date_placed_ceased Na, they fail even if their total NAs is 1
        df_ordered = df.sort_values("DATE_PLACED", ascending=False)
        df_ordered.drop_duplicates("CHILD", keep="first", inplace=True)
        df_ordered_index = list(df_ordered.index)
        df_dropped_recent = df[
            (~df.index.isin(df_ordered_index)) & df["DATE_PLACED_CEASED"].isna()
        ]
        non_recent_nans = list(df_dropped_recent.index)

        error_mask = df.index.isin(too_many_nans_index) | df.index.isin(non_recent_nans)
        return {"PlacedAdoption": df.index[error_mask].to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "02/02/2020",
            },  # 0 pass
            {
                "CHILD": "child1",
                "DATE_PLACED": "03/02/2020",
                "DATE_PLACED_CEASED": "04/02/2020",
            },  # 1 pass
            {
                "CHILD": "child2",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": pd.NA,
            },  # 2 fail
            {
                "CHILD": "child2",
                "DATE_PLACED": "02/02/2020",
                "DATE_PLACED_CEASED": pd.NA,
            },  # 3 fail
            {
                "CHILD": "child3",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "02/02/2020",
            },  # 4 pass
            {
                "CHILD": "child3",
                "DATE_PLACED": "03/02/2020",
                "DATE_PLACED_CEASED": pd.NA,
            },  # 5 pass
            {
                "CHILD": "child4",
                "DATE_PLACED": "01/02/2020",
                "DATE_PLACED_CEASED": "02/02/2020",
            },  # 6 pass
            {
                "CHILD": "child4",
                "DATE_PLACED": "01/01/2020",
                "DATE_PLACED_CEASED": pd.NA,
            },  # 7 fail
        ]
    )

    fake_data["DATE_PLACED"] = pd.to_datetime(
        fake_data["DATE_PLACED"], format="%d/%m/%Y"
    )
    fake_data["DATE_PLACED_CEASED"] = pd.to_datetime(
        fake_data["DATE_PLACED_CEASED"], format="%d/%m/%Y"
    )

    fake_dfs = {"PlacedAdoption": fake_data}

    assert validate(fake_dfs) == {"PlacedAdoption": [2, 3, 7]}
