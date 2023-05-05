from validator903.types import ErrorDefinition


@rule_definition(
    code="120",
    message="The reason for the reversal of the decision that the child should be placed for adoption code is not valid.",
    affected_fields=["REASON_PLACED_CEASED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}

    placedadoptions = dfs["PlacedAdoption"]
    codelist = ["RD1", "RD2", "RD3", "RD4"]

    mask = (
        placedadoptions["REASONPLACEDCEASED"].isin(codelist)
        | placedadoptions["REASONPLACEDCEASED"].isna()
    )

    validationerrormask = ~mask
    validationerrorlocations = placedadoptions.index[validationerrormask]

    return {"PlacedAdoption": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REASON_PLACED_CEASED": ["rd1", "RD0", 1, "RD1", "", pd.NA],
        }
    )

    fake_dfs = {"PlacedAdoption": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"PlacedAdoption": [0, 1, 2, 4]}
