import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="559",
    message="Date of decision that a child should be placed for adoption was not in the current year but the date of the decision that the child should be placed for adoption was not completed in a previous return.",
    affected_fields=["DATE_PLACED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs or "PlacedAdoptionlast" not in dfs:
        return {}
    else:
        placedadoption = dfs["PlacedAdoption"]
        palast = dfs["PlacedAdoptionlast"]
        collectionstart = dfs["metadata"]["collectionstart"]

        # convert dates to appropriate format
        palast["DATEPLACED"] = pd.todatetime(
            palast["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        placedadoption["DATEPLACED"] = pd.todatetime(
            placedadoption["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )

        # prepare to merge
        placedadoption.resetindex(inplace=True)
        palast.resetindex(inplace=True)
        merged = placedadoption.merge(
            palast, how="left", on="CHILD", suffixes=["now", "last"]
        )

        # If <DATEPLACED> < <COLLECTIONSTARTDATE> then <CURRENTCOLLECTIONYEAR> -1 <DATEPLACED> cannot be Null
        mask = (merged["DATEPLACEDnow"] < collectionstart) & merged[
            "DATEPLACEDlast"
        ].isna()
        # error locations
        errorlocs = merged.loc[mask, "indexnow"]
        return {"PlacedAdoption": errorlocs.tolist()}


def test_validate():
    import pandas as pd

    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}
    fake_placed_adoption = pd.DataFrame(
        [
            {"CHILD": 101, "DATE_PLACED": "26/05/2022"},  # 0
            {"CHILD": 102, "DATE_PLACED": "26/05/2021"},  # 1
            {"CHILD": 103, "DATE_PLACED": pd.NA},  # 2
            {"CHILD": 104, "DATE_PLACED": "01/02/2016"},  # 3
            {"CHILD": 105, "DATE_PLACED": "26/05/2019"},  # 4
        ]
    )
    fake_last_pa = pd.DataFrame(
        [
            {"CHILD": 101, "DATE_PLACED": "26/05/2000"},  # 0
            {"CHILD": 102, "DATE_PLACED": pd.NA},  # 1
            {"CHILD": 103, "DATE_PLACED": "26/05/2000"},  # 2
            {"CHILD": 104, "DATE_PLACED": "01/02/2016"},  # 3
            {"CHILD": 105, "DATE_PLACED": pd.NA},  # 4
        ]
    )
    fake_dfs = {
        "PlacedAdoption": fake_placed_adoption,
        "PlacedAdoption_last": fake_last_pa,
        "metadata": metadata,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {
        "PlacedAdoption": [
            4,
        ]
    }
