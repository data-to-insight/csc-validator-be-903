from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="143",
    message="The reason for new episode code is not a valid code.",
    affected_fields=["RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    code_list = ["S", "P", "L", "T", "U", "B"]

    mask = episodes["RNE"].isin(code_list) | episodes["RNE"].isna()

    validation_error_mask = ~mask
    validation_error_locations = episodes.index[validation_error_mask]

    return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "RNE": ["S", "p", "SP", "a", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [1, 2, 3, 4]}
