import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


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
        adt["DATE_MATCH"] = pd.to_datetime(
            adt["DATE_MATCH"], format="%d/%m/%Y", errors="coerce"
        )
        adt["DATE_INT"] = pd.to_datetime(
            adt["DATE_INT"], format="%d/%m/%Y", errors="coerce"
        )

        # If <DATE_MATCH> provided, then <DATE_INT> must also be provided and be <= <DATE_MATCH>
        mask1 = adt["DATE_MATCH"].notna() & adt["DATE_INT"].isna()
        mask2 = (
            adt["DATE_MATCH"].notna()
            & adt["DATE_INT"].notna()
            & (adt["DATE_INT"] > adt["DATE_MATCH"])
        )
        mask = mask1 | mask2

        return {"AD1": adt.index[mask].to_list()}


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

    

    result = validate(fake_dfs)

    assert result == {"AD1": [2, 3, 4]}
