from validator903.types import ErrorDefinition


@rule_definition(
    code="561",
    message="Date of the decision that the child should be placed for adoption this year is the same as that recorded last year but records show that the decision changed, and the child should no longer be placed for adoption last year.",
    affected_fields=["DATE_PLACED"],
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

        # If <CURRENTCOLLECTIONYEAR> <DATEPLACED> is = <CURRENTCOLLECTIONYEAR> -1 <DATEPLACED> then <CURRENTCOLLECTIONYEAR> -1 <DATEPLACEDCEASED> and <REASONPLACEDCEASED> should be Null
        mask = (merged["DATEPLACEDnow"] == merged["DATEPLACEDlast"]) & merged[
            ["REASONPLACEDCEASEDlast", "DATEPLACEDCEASEDlast"]
        ].notna().any(axis=1)

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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"PlacedAdoption": [0, 1, 3]}
