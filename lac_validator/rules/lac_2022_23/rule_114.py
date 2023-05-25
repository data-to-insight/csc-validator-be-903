from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="114",
    message="Data entry to record the status of former carer(s) of an adopted child is invalid.",
    affected_fields=["FOSTER_CARE"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    code_list = ["0", "1"]

    mask = (
        adoptions["FOSTER_CARE"].astype(str).isin(code_list)
        | adoptions["FOSTER_CARE"].isna()
    )

    validation_error_mask = ~mask
    validation_error_locations = adoptions.index[validation_error_mask]

    return {"AD1": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "FOSTER_CARE": [0, 1, "0", "1", 2, "former foster carer", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"AD1": [4, 5, 6]}
