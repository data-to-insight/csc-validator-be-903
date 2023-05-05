from validator903.types import ErrorDefinition


@rule_definition(
    code="563",
    message="The child should no longer be placed for adoption but the date of the decision that the child should be placed for adoption is blank",
    affected_fields=["DATE_PLACED", "REASON_PLACED_CEASED", "DATE_PLACED_CEASED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        placedadoption = dfs["PlacedAdoption"]
        mask = (
            placedadoption["REASONPLACEDCEASED"].notna()
            & placedadoption["DATEPLACEDCEASED"].notna()
            & placedadoption["DATEPLACED"].isna()
        )
        errorlocations = placedadoption.index[mask]
        return {"PlacedAdoption": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_placed = pd.DataFrame(
        [
            {
                "CHILD": "11",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2000",
            },  # 0
            {
                "CHILD": "202",
                "DATE_PLACED_CEASED": "01/02/2003",
                "REASON_PLACED_CEASED": "invalid dont matter",
                "DATE_PLACED": "26/05/2000",
            },  # 1
            {
                "CHILD": "3003",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2000",
            },  # 2
            {
                "CHILD": "40004",
                "DATE_PLACED_CEASED": "26/05/2001",
                "REASON_PLACED_CEASED": "some sample reason",
                "DATE_PLACED": pd.NA,
            },  # 3: Fail
            {
                "CHILD": "606",
                "DATE_PLACED_CEASED": pd.NA,
                "REASON_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2000",
            },  # 4
        ]
    )

    fake_dfs = {"PlacedAdoption": fake_placed}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"PlacedAdoption": [3]}
