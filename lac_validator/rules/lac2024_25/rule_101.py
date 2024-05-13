import pandas as pd

from lac_validator.rule_engine import rule_definition


# https://assets.publishing.service.gov.uk/media/660d1758fb0f77001aec66de/CLA_SSDA903_2023-24_Validation_rules.pdf
# Gender code is not valid

# The gender data item must be either: 1 = male or 2 = female.

# <SEX> must be provided and be a valid value


@rule_definition(
    code="101",  # Error code (from above guidance)
    message="Gender code is not valid",  # Msg shown on validation report
    affected_fields=["SEX"],
)


def validate(dfs):
    if "Header" not in dfs:
        return {}

    header = dfs["Header"]
    valid_code_list = ["1", "2"] # 1 = male or 2 = female.

    is_valid_sex_code = (
        header["SEX"].astype(str).isin(valid_code_list)
    )  # "SEX" column to str chk if vals in valid codes lst

    validation_error_mask = ~is_valid_sex_code  # id rows where the "SEX" val invalid

    validation_error_locations = header.index[
        validation_error_mask
    ].tolist()  # get list of idx of validation errors

    return {"Header": validation_error_locations}




def test_validate():
    import pandas as pd

    fake_data_df = pd.DataFrame(
        {
            "SEX": [
                1,  # valid male
                2,  # valid female
                3,  # invalid
                "",  # invalid, no data
                pd.NA,  # invalid, recognised null
            ],
        }
    )

    fake_dfs = {"Header": fake_data_df}

    result = validate(fake_dfs)

    assert result == {"Header": [2, 3, 4]}
