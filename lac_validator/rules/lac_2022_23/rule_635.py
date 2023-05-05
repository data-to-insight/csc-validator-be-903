from validator903.types import ErrorDefinition


@rule_definition(
    code="635",
    message="There are entries for date of order and local authority code where previous permanence option was arranged but previous permanence code is Z1",
    affected_fields=["LA_PERM", "DATE_PERM", "PREV_PERM"],
)
def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}
    else:
        prevperm = dfs["PrevPerm"]
        # raise and error if either LAPERM or DATEPERM are present, yet PREVPERM is absent.
        mask = (prevperm["LAPERM"].notna() | prevperm["DATEPERM"].notna()) & prevperm[
            "PREVPERM"
        ].isna()

        errorlocations = prevperm.index[mask]
    return {"PrevPerm": errorlocations.tolist()}


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
