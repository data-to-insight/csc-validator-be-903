import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="176",
    message="The gender of adopter(s) at the date of adoption code is not a valid code.",
    affected_fields=["SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    code_list = ["M1", "F1", "MM", "FF", "MF"]

    mask = adoptions["SEX_ADOPTR"].isin(code_list) | adoptions["SEX_ADOPTR"].isna()

    validation_error_mask = ~mask
    validation_error_locations = adoptions.index[validation_error_mask]

    return {"AD1": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX_ADOPTR": ["m1", "F1", "MM", "1", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    result = validate(fake_dfs)

    assert result == {"AD1": [0, 3, 4]}
