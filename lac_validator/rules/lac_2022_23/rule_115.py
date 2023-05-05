import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="115",
    message="Date of Local Authority's (LA) decision that a child should be placed for adoption is not a valid date.",
    affected_fields=["DATE_PLACED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        adopt = dfs["PlacedAdoption"]
        mask = pd.todatetime(
            adopt["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        ).notna()

        nalocation = adopt["DATEPLACED"].isna()

        validationerrormask = ~mask & ~nalocation
        validationerrorlocations = adopt.index[validationerrormask]

        return {"PlacedAdoption": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_PLACED": [
                "01/01/2021",
                "19/02/2010",
                "38/04/2019",
                "01/01/19",
                pd.NA,
            ],
        }
    )

    fake_dfs = {"PlacedAdoption": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"PlacedAdoption": [2, 3]}
