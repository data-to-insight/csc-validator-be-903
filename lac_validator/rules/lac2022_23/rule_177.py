import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="177",
    message="The legal status of adopter(s) code is not a valid code.",
    affected_fields=["LS_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    code_list = ["L0", "L11", "L12", "L2", "L3", "L4"]

    mask = adoptions["LS_ADOPTR"].isin(code_list) | adoptions["LS_ADOPTR"].isna()

    validation_error_mask = ~mask
    validation_error_locations = adoptions.index[validation_error_mask]

    return {"AD1": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L0", "L11", "L1", "l2", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    result = validate(fake_dfs)

    assert result == {"AD1": [2, 3, 4]}
