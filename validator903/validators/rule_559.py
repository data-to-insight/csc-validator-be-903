import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="559",
        description="Date of decision that a child should be placed for adoption was not in the current year but the date of the decision that the child should be placed for adoption was not completed in a previous return.",
        affected_fields=["DATE_PLACED"],
    )

    def _validate(dfs):
        if "PlacedAdoption" not in dfs or "PlacedAdoption_last" not in dfs:
            return {}
        else:
            placed_adoption = dfs["PlacedAdoption"]
            pa_last = dfs["PlacedAdoption_last"]
            collection_start = dfs["metadata"]["collection_start"]

            # convert dates to appropriate format
            pa_last["DATE_PLACED"] = pd.to_datetime(
                pa_last["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
            )
            placed_adoption["DATE_PLACED"] = pd.to_datetime(
                placed_adoption["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
            )
            collection_start = pd.to_datetime(
                collection_start, format="%d/%m/%Y", errors="coerce"
            )

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            pa_last.reset_index(inplace=True)
            merged = placed_adoption.merge(
                pa_last, how="left", on="CHILD", suffixes=["_now", "_last"]
            )

            # If <DATE_PLACED> < <COLLECTION_START_DATE> then <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED> cannot be Null
            mask = (merged["DATE_PLACED_now"] < collection_start) & merged[
                "DATE_PLACED_last"
            ].isna()
            # error locations
            error_locs = merged.loc[mask, "index_now"]
            return {"PlacedAdoption": error_locs.tolist()}

    return error, _validate


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
