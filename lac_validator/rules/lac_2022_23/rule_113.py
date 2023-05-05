import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="113",
    message="Date matching child and adopter(s) is not a valid date.",
    affected_fields=["DATE_MATCH"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        ad1 = dfs["AD1"]
        mask = pd.todatetime(
            ad1["DATEMATCH"], format="%d/%m/%Y", errors="coerce"
        ).notna()

        nalocation = ad1["DATEMATCH"].isna()

        validationerrormask = ~mask & ~nalocation
        validationerrorlocations = ad1.index[validationerrormask]

        return {"AD1": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_MATCH": ["22/11/2015", "08/05/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [2, 3]}
