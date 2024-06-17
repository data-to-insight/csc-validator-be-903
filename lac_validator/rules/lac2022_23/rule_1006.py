import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1006",
    message="Missing type invalid.",
    affected_fields=["MISSING"],
    tables=["Missing"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}

    missing_from_care = dfs["Missing"]
    code_list = ["M", "A"]

    mask = (
        missing_from_care["MISSING"].isin(code_list)
        | missing_from_care["MISSING"].isna()
    )

    validation_error_mask = ~mask
    validation_error_locations = missing_from_care.index[validation_error_mask]

    return {"Missing": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MISSING": ["M", "A", "AWAY", "NA", "", pd.NA, "m"],
        }
    )

    fake_dfs = {"Missing": fake_data}

    result = validate(fake_dfs)

    assert result == {"Missing": [2, 3, 4, 6]}
