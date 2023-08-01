import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="102",
    message="Date of birth is not a valid date.",
    affected_fields=["DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        mask = pd.to_datetime(header["DOB"], format="%d/%m/%Y", errors="coerce").notna()

        validation_error_mask = ~mask
        validation_error_locations = header.index[validation_error_mask]

        return {"Header": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOB": ["01/01/2021", "19/02/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"Header": [2, 3, 4]}
