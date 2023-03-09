import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="522",
        description="Date of decision that the child should be placed for adoption must be on or before the date that a child should no longer be placed for adoption.",
        affected_fields=["DATE_PLACED", "DATE_PLACED_CEASED"],
    )

    def _validate(dfs):
        if "PlacedAdoption" not in dfs:
            return {}
        else:
            placed_adoption = dfs["PlacedAdoption"]
            # Convert to datetimes
            placed_adoption["DATE_PLACED_CEASED"] = pd.to_datetime(
                placed_adoption["DATE_PLACED_CEASED"],
                format="%d/%m/%Y",
                errors="coerce",
            )
            placed_adoption["DATE_PLACED"] = pd.to_datetime(
                placed_adoption["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
            )
            # Boolean mask
            mask = (
                placed_adoption["DATE_PLACED_CEASED"] < placed_adoption["DATE_PLACED"]
            )

            error_locations = placed_adoption.index[mask]
            return {"PlacedAdoption": error_locations.to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_placed_data = pd.DataFrame(
        [
            {
                "CHILD": "11",
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": "26/05/2000",
            },  # 0
            {
                "CHILD": "202",
                "DATE_PLACED_CEASED": "01/02/2003",
                "DATE_PLACED": "26/05/2000",
            },  # 1
            {
                "CHILD": "3003",
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": pd.NA,
            },  # 2
            {
                "CHILD": "40004",
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": "01/02/2003",
            },  # 3 Fail
            {
                "CHILD": "606",
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2000",
            },  # 4
        ]
    )
    fake_dfs = {"PlacedAdoption": fake_placed_data}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"PlacedAdoption": [3]}
