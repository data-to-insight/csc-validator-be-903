from validator903.types import ErrorDefinition


@rule_definition(
    code="612",
    message="Date of birth field has been completed but mother field indicates child is not a mother.",
    affected_fields=["SEX", "MOTHER", "MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]

        errormask = (
            ((header["MOTHER"].astype(str) == "0") | header["MOTHER"].isna())
            & (header["SEX"].astype(str) == "2")
            & header["MCDOB"].notna()
        )

        validationerrorlocations = header.index[errormask]

        return {"Header": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": [2, "2", "2", 2, 2, 1, 1, 1, "2"],
            "MOTHER": ["0", "0", pd.NA, pd.NA, 1, 0, 1, pd.NA, pd.NA],
            "MC_DOB": [
                "19/02/2016",
                "dd/mm/yyyy",
                "31/31/19",
                pd.NA,
                "19/02/2019",
                pd.NA,
                "12/10/2010",
                "21/3rd/yYyYyY",
                "21/3rd/yYyYyY",
            ],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [0, 1, 2, 8]}
