from validator903.types import ErrorDefinition


@rule_definition(
    code="174",
    message="Mother's child date of birth is recorded but gender shows that the child is a male.",
    affected_fields=["SEX", "MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]

        childismale = header["SEX"].astype(str) == "1"
        mcdobrecorded = header["MCDOB"].notna()

        errormask = childismale & mcdobrecorded

        validationerrorlocations = header.index[errormask]

        return {"Header": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": ["1", "1", "2", "2", 1, 1],
            "MC_DOB": [pd.NA, "19/02/2010", pd.NA, "19/02/2010", pd.NA, "19/02/2010"],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 5]}
