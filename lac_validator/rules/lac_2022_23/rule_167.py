from validator903.types import ErrorDefinition


@rule_definition(
    code="167",
    message="Data entry for participation is invalid or blank.",
    affected_fields=["REVIEW_CODE"],
)
def validate(dfs):
    if "Reviews" not in dfs:
        return {}

    review = dfs["Reviews"]
    codelist = ["PN0", "PN1", "PN2", "PN3", "PN4", "PN5", "PN6", "PN7"]

    mask = (
        review["REVIEW"].notna() & review["REVIEWCODE"].isin(codelist)
        | review["REVIEW"].isna() & review["REVIEWCODE"].isna()
    )

    validationerrormask = ~mask
    validationerrorlocations = review.index[validationerrormask]

    return {"Reviews": validationerrorlocations.tolist()}


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
