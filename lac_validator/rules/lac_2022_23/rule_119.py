from validator903.types import ErrorDefinition


@rule_definition(
    code="119",
    message="If the decision is made that a child should no longer be placed for adoption, then the date of this decision and the reason why this decision was made must be completed.",
    affected_fields=["REASON_PLACED_CEASED", "DATE_PLACED_CEASED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        adopt = dfs["PlacedAdoption"]
        naplacedceased = adopt["DATEPLACEDCEASED"].isna()
        nareasonceased = adopt["REASONPLACEDCEASED"].isna()

        validationerror = (naplacedceased & ~nareasonceased) | (
            ~naplacedceased & nareasonceased
        )
        validationerrorlocations = adopt.index[validationerror]

        return {"PlacedAdoption": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_PLACED_CEASED": ["22/11/2015", "08/05/2010", pd.NA, pd.NA],
            "REASON_PLACED_CEASED": ["XXX", pd.NA, "10/05/2009", pd.NA],
        }
    )

    fake_dfs = {"PlacedAdoption": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"PlacedAdoption": [1, 2]}
