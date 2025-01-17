import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="101",
    message="The child or young person’s reported sex is not valid.",
    affected_fields=["SEX"],
    tables=["Header"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}

    header = dfs["Header"]
    code_list = ["M", "F", "U"]

    mask = header["SEX"].astype(str).isin(code_list)

    validation_error_mask = ~mask
    validation_error_locations = header.index[validation_error_mask]

    return {"Header": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": ["M", "F", "U", 1, "X", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    result = validate(fake_dfs)

    assert result == {"Header": [3, 4, 5]}
