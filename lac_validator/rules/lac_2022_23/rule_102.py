import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="102",
    message="Date of birth is not a valid date.",
    affected_fields=["DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        mask = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce").notna()

        validationerrormask = ~mask
        validationerrorlocations = header.index[validationerrormask]

        return {"Header": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOB": ["01/01/2021", "19/02/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [2, 3, 4]}
