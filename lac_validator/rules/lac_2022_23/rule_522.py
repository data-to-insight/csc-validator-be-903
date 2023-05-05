import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="522",
    message="Date of decision that the child should be placed for adoption must be on or before the date that a child should no longer be placed for adoption.",
    affected_fields=["DATE_PLACED", "DATE_PLACED_CEASED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        placedadoption = dfs["PlacedAdoption"]
        # Convert to datetimes
        placedadoption["DATEPLACEDCEASED"] = pd.todatetime(
            placedadoption["DATEPLACEDCEASED"],
            format="%d/%m/%Y",
            errors="coerce",
        )
        placedadoption["DATEPLACED"] = pd.todatetime(
            placedadoption["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        # Boolean mask
        mask = placedadoption["DATEPLACEDCEASED"] < placedadoption["DATEPLACED"]

        errorlocations = placedadoption.index[mask]
        return {"PlacedAdoption": errorlocations.tolist()}


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
