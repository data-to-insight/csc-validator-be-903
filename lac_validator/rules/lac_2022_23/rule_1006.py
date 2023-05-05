from validator903.types import ErrorDefinition


@rule_definition(
    code="1006",
    message="Missing type invalid.",
    affected_fields=["MISSING"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}

    missingfromcare = dfs["Missing"]
    codelist = ["M", "A"]

    mask = missingfromcare["MISSING"].isin(codelist) | missingfromcare["MISSING"].isna()

    validationerrormask = ~mask
    validationerrorlocations = missingfromcare.index[validationerrormask]

    return {"Missing": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MISSING": ["M", "A", "AWAY", "NA", "", pd.NA],
        }
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [2, 3, 4]}
