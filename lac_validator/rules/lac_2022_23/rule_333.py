import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="333",
    message="Date should be placed for adoption must be on or prior to the date of matching child with adopter(s).",
    affected_fields=["DATE_INT"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        adt = dfs["AD1"]
        adt["DATEMATCH"] = pd.todatetime(
            adt["DATEMATCH"], format="%d/%m/%Y", errors="coerce"
        )
        adt["DATEINT"] = pd.todatetime(
            adt["DATEINT"], format="%d/%m/%Y", errors="coerce"
        )

        # If <DATEMATCH> provided, then <DATEINT> must also be provided and be <= <DATEMATCH>
        mask1 = adt["DATEMATCH"].notna() & adt["DATEINT"].isna()
        mask2 = (
            adt["DATEMATCH"].notna()
            & adt["DATEINT"].notna()
            & (adt["DATEINT"] > adt["DATEMATCH"])
        )
        mask = mask1 | mask2

        return {"AD1": adt.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_adt = pd.DataFrame(
        [
            {"DATE_INT": "01/06/2020", "DATE_MATCH": "05/06/2020"},  # 0
            {"DATE_INT": "02/06/2020", "DATE_MATCH": pd.NA},  # 1
            {"DATE_INT": "03/06/2020", "DATE_MATCH": "01/06/2020"},  # 2  Fails
            {"DATE_INT": "04/06/2020", "DATE_MATCH": "02/06/2020"},  # 3  Fails
            {"DATE_INT": pd.NA, "DATE_MATCH": "05/06/2020"},  # 4  Fails
        ]
    )

    fake_dfs = {"AD1": fake_adt}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [2, 3, 4]}
