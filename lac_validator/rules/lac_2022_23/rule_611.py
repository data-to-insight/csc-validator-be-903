from validator903.types import ErrorDefinition


@rule_definition(
    code="611",
    message="Date of birth field is blank, but child is a mother.",
    affected_fields=["MOTHER", "MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        validationerrormask = (
            header["MOTHER"].astype(str).isin(["1"]) & header["MCDOB"].isna()
        )
        validationerrorlocations = header.index[validationerrormask]

        return {"Header": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MOTHER": [1, "1", pd.NA, pd.NA, 1],
            "MC_DOB": ["01/01/2021", "19/02/2016", "dd/mm/yyyy", "31/31/19", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [4]}
