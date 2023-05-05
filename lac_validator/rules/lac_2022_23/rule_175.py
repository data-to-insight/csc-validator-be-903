from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="175",
    message="The number of adopter(s) code is not a valid code.",
    affected_fields=["NB_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    code_list = ["1", "2"]

    mask = (
        adoptions["NB_ADOPTR"].astype(str).isin(code_list)
        | adoptions["NB_ADOPTR"].isna()
    )

    validation_error_mask = ~mask
    validation_error_locations = adoptions.index[validation_error_mask]

    return {"AD1": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "NB_ADOPTR": [0, 1, 2, "1", "2", "0", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [0, 5, 6]}
