from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="101",
    message="Gender code is not valid.",
    affected_fields=["SEX"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}

    header = dfs["Header"]
    code_list = ["1", "2"]

    mask = header["SEX"].astype(str).isin(code_list)

    validation_error_mask = ~mask
    validation_error_locations = header.index[validation_error_mask]

    return {"Header": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": [1, 2, 3, pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"Header": [2, 3]}
