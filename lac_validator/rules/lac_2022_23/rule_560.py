from validator903.types import ErrorDefinition


@rule_definition(
    code="560",
    message="Date of decision that the child should be placed for adoption this year is different from that recorded last year but the decision to place the child for adoption did not change.",
    affected_fields=["DATE_PLACED", "DATE_PLACED_CEASED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs or "PlacedAdoptionlast" not in dfs:
        return {}
    else:
        placedadoption = dfs["PlacedAdoption"]
        palast = dfs["PlacedAdoptionlast"]

        # prepare to merge
        placedadoption.resetindex(inplace=True)
        palast.resetindex(inplace=True)
        merged = placedadoption.merge(
            palast, how="inner", on="CHILD", suffixes=["now", "last"]
        )

        # If <CURRENTCOLLECTIONYEAR> -1 <DATEPLACED> has been provided and <DATEPLACEDCEASED> is Null then <CURRENTCOLLECTIONYEAR> <DATEPLACED> should = <CURRENTCOLLECTIONYEAR> -1 <DATEPLACED>
        mask = (
            merged["DATEPLACEDlast"].notna()
            & merged["DATEPLACEDCEASEDlast"].isna()
            & (merged["DATEPLACEDnow"] != merged["DATEPLACEDlast"])
        )
        # error locations
        errorlocs = merged.loc[mask, "indexnow"]
        return {"PlacedAdoption": errorlocs.tolist()}


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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"PlacedAdoption": [0, 4]}
