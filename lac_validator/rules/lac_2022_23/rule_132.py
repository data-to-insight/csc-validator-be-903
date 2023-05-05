from validator903.types import ErrorDefinition


@rule_definition(
    code="132",
    message="Data entry for activity after leaving care is invalid.",
    affected_fields=["ACTIV"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}

    careleavers = dfs["OC3"]
    codelist = [
        "F1",
        "P1",
        "F2",
        "P2",
        "F4",
        "P4",
        "F5",
        "P5",
        "G4",
        "G5",
        "G6",
        "0",
    ]
    mask = careleavers["ACTIV"].astype(str).isin(codelist)

    validationerrormask = ~mask
    validationerrorlocations = careleavers.index[validationerrormask]

    return {"OC3": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "ACTIV": ["f1", "F1", 1, 0, "1", "0", "", pd.NA],
        }
    )

    fake_dfs = {"OC3": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [0, 2, 4, 6, 7]}
