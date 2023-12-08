import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="174",
    message="Mother's child date of birth is recorded but sex shows that the child is a male.",
    affected_fields=["SEX", "MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]

        child_is_male = header["SEX"] == "M"
        mc_dob_recorded = header["MC_DOB"].notna()

        error_mask = child_is_male & mc_dob_recorded

        validation_error_locations = header.index[error_mask]

        return {"Header": validation_error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": ["M", "M", "F", "F", "M", "M"],
            "MC_DOB": [pd.NA, "19/02/2010", pd.NA, "19/02/2010", pd.NA, "19/02/2010"],
        }
    )

    fake_dfs = {"Header": fake_data}

    result = validate(fake_dfs)

    assert result == {"Header": [1, 5]}
