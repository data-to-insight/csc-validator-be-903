import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="561",
    message="Date of the decision that the child should be placed for adoption this year is the same as that recorded last year but records show that the decision changed, and the child should no longer be placed for adoption last year.",
    affected_fields=["DATE_PLACED"],
    tables=["PlacedAdoption", "PlacedAdoption_last"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs or "PlacedAdoption_last" not in dfs:
        return {}
    else:
        placed_adoption = dfs["PlacedAdoption"]
        pa_last = dfs["PlacedAdoption_last"]

        # prepare to merge
        placed_adoption.reset_index(inplace=True)
        pa_last.reset_index(inplace=True)
        merged = placed_adoption.merge(
            pa_last, how="inner", on="CHILD", suffixes=["_now", "_last"]
        )

        # If <CURRENT_COLLECTION_YEAR> <DATE_PLACED> is = <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED> then <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED_CEASED> and <REASON_PLACED_CEASED> should be Null
        mask = (merged["DATE_PLACED_now"] == merged["DATE_PLACED_last"]) & merged[
            ["REASON_PLACED_CEASED_last", "DATE_PLACED_CEASED_last"]
        ].notna().any(axis=1)

        # error locations
        error_locs = merged.loc[mask, "index_now"]
        return {"PlacedAdoption": error_locs.tolist()}


def test_validate():
    import pandas as pd

    fake_placed_adoption = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": "26/05/2019",
                "REASON_PLACED_CEASED": "xx",
            },
            # 0
            {
                "CHILD": 102,
                "DATE_PLACED_CEASED": "01/07/2018",
                "DATE_PLACED": "26/05/2000",
                "REASON_PLACED_CEASED": "xx",
            },
            # 1
            {
                "CHILD": 103,
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": pd.NA,
                "REASON_PLACED_CEASED": "xx",
            },  # 2
            {
                "CHILD": 104,
                "DATE_PLACED_CEASED": "26/05/2017",
                "DATE_PLACED": "01/02/2016",
                "REASON_PLACED_CEASED": "xx",
            },
            # 3
            {
                "CHILD": 106,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2029",
                "REASON_PLACED_CEASED": "xx",
            },  # 4
        ]
    )

    fake_pa_last = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2019",
                "REASON_PLACED_CEASED": "xx",
            },
            # 0 fail
            {
                "CHILD": 102,
                "DATE_PLACED_CEASED": "01/07/2018",
                "DATE_PLACED": "26/05/2000",
                "REASON_PLACED_CEASED": "xx",
            },
            # 1 fail
            {
                "CHILD": 103,
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": pd.NA,
                "REASON_PLACED_CEASED": "xx",
            },  # 2
            {
                "CHILD": 104,
                "DATE_PLACED_CEASED": "26/05/2017",
                "DATE_PLACED": "01/02/2016",
                "REASON_PLACED_CEASED": "xx",
            },
            # 3
            {
                "CHILD": 105,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2019",
                "REASON_PLACED_CEASED": pd.NA,
            },
            # 4 pass
            {
                "CHILD": 106,
                "DATE_PLACED_CEASED": "xx",
                "DATE_PLACED": "01/07/2019",
                "REASON_PLACED_CEASED": "xx",
            },
            # 5 pass
        ]
    )

    fake_dfs = {
        "PlacedAdoption": fake_placed_adoption,
        "PlacedAdoption_last": fake_pa_last,
    }

    result = validate(fake_dfs)
    assert result == {"PlacedAdoption": [0, 1, 3]}
