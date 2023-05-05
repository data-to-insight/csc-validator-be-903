import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="621",
    message="Mother’s field has been completed but date of birth shows that the mother is younger than her child.",
    affected_fields=["DOB", "MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]

        header["MCDOB"] = pd.todatetime(
            header["MCDOB"], format="%d/%m/%Y", errors="coerce"
        )
        header["DOB"] = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce")
        mask = (header["MCDOB"] > header["DOB"]) | header["MCDOB"].isna()

        validationerrormask = ~mask
        validationerrorlocations = header.index[validationerrormask]

        return {"Header": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOB": [
                "01/12/2021",
                "19/02/2016",
                "31/01/2019",
                "31/01/2019",
                "31/01/2019",
            ],
            "MC_DOB": ["01/01/2021", "19/12/2016", "31/01/2019", pd.NA, "01/02/2019"],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [0, 2]}
