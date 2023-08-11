import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="560",
    message="Date of decision that the child should be placed for adoption this year is different from that recorded last year but the decision to place the child for adoption did not change.",
    affected_fields=["DATE_PLACED", "DATE_PLACED_CEASED"],
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

        # If <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED> has been provided and <DATE_PLACED_CEASED> is Null then <CURRENT_COLLECTION_YEAR> <DATE_PLACED> should = <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED>
        mask = (
            merged["DATE_PLACED_last"].notna()
            & merged["DATE_PLACED_CEASED_last"].isna()
            & (merged["DATE_PLACED_now"] != merged["DATE_PLACED_last"])
        )
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
            },  # 0 --- FAIL
            {
                "CHILD": 102,
                "DATE_PLACED_CEASED": "01/07/2018",
                "DATE_PLACED": "26/05/2000",
            },  # 1
            {
                "CHILD": 103,
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": pd.NA,
            },  # 2
            {
                "CHILD": 104,
                "DATE_PLACED_CEASED": "26/05/2017",
                "DATE_PLACED": "01/02/2016",
            },  # 3
            {
                "CHILD": 105,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "27/05/2019",
            },  # 4 --- FAIL
            {
                "CHILD": 106,
                "DATE_PLACED_CEASED": "34rd/Dec/-1000A.D",
                "DATE_PLACED": "34rd/Dec/-1000A.D",
            },  # 5
            {
                "CHILD": 107,
                "DATE_PLACED_CEASED": "different",
                "DATE_PLACED": "also different",
            },  # 6
        ]
    )
    fake_pa_last = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2000",
            },  # 0
            {
                "CHILD": 102,
                "DATE_PLACED_CEASED": "01/07/2018",
                "DATE_PLACED": "26/05/2000",
            },  # 1
            {
                "CHILD": 103,
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": pd.NA,
            },  # 2
            {
                "CHILD": 104,
                "DATE_PLACED_CEASED": "26/05/2017",
                "DATE_PLACED": "01/02/2016",
            },  # 3
            {
                "CHILD": 105,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2019",
            },  # 4
            {
                "CHILD": 106,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "34rd/Dec/-1000A.D",
            },  # 5
            {
                "CHILD": 107,
                "DATE_PLACED_CEASED": "34rd/Dec/-1000A.D",
                "DATE_PLACED": "20/20/2020",
            },  # 6
        ]
    )
    fake_dfs = {
        "PlacedAdoption": fake_placed_adoption,
        "PlacedAdoption_last": fake_pa_last,
    }

    result = validate(fake_dfs)
    assert result == {"PlacedAdoption": [0, 4]}
