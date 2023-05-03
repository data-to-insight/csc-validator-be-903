from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="167",
        description="Data entry for participation is invalid or blank.",
        affected_fields=["REVIEW_CODE"],
    )

    def _validate(dfs):
        if "Reviews" not in dfs:
            return {}

        review = dfs["Reviews"]
        code_list = ["PN0", "PN1", "PN2", "PN3", "PN4", "PN5", "PN6", "PN7"]

        mask = (
            review["REVIEW"].notna() & review["REVIEW_CODE"].isin(code_list)
            | review["REVIEW"].isna() & review["REVIEW_CODE"].isna()
        )

        validation_error_mask = ~mask
        validation_error_locations = review.index[validation_error_mask]

        return {"Reviews": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REVIEW": ["01/02/2020", "31/03/2020", "12/12/2019", "05/07/2020", pd.NA],
            "REVIEW_CODE": ["p0", "child too young", "PN3", "", pd.NA],
        }
    )

    fake_dfs = {"Reviews": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Reviews": [0, 1, 3]}
