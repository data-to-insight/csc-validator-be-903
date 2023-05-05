from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="635",
    message="There are entries for date of order and local authority code where previous permanence option was arranged but previous permanence code is Z1",
    affected_fields=["LA_PERM", "DATE_PERM", "PREV_PERM"],
)
def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}
    else:
        prev_perm = dfs["PrevPerm"]
        # raise and error if either LA_PERM or DATE_PERM are present, yet PREV_PERM is absent.
        mask = (
            prev_perm["LA_PERM"].notna() | prev_perm["DATE_PERM"].notna()
        ) & prev_perm["PREV_PERM"].isna()

        error_locations = prev_perm.index[mask]
    return {"PrevPerm": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data_prevperm = pd.DataFrame(
        {
            "CHILD": ["2", "4", "5", "6", "7", "8"],
            "PREV_PERM": ["Z1", pd.NA, pd.NA, "Z1", pd.NA, "P1"],
            "LA_PERM": [pd.NA, "352", pd.NA, "352", pd.NA, "352"],
            "DATE_PERM": [pd.NA, pd.NA, "01/05/2000", pd.NA, pd.NA, "05/05/2020"],
        }
    )

    fake_dfs = {"PrevPerm": fake_data_prevperm}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"PrevPerm": [1, 2]}
