from validator903.types import ErrorDefinition


@rule_definition(
    code="525",
    message="A child for whom the decision to be placed for adoption has been reversed cannot be adopted during the year.",
    affected_fields=[
        "DATE_PLACED_CEASED",
        "DATE_INT",
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs or "AD1" not in dfs:
        return {}
    else:
        placedadoption = dfs["PlacedAdoption"]
        ad1 = dfs["AD1"]
        # prepare to merge
        placedadoption.resetindex(inplace=True)
        ad1.resetindex(inplace=True)

        merged = placedadoption.merge(
            ad1, on="CHILD", how="left", suffixes=["placed", "ad1"]
        )
        # If <DATEPLACEDCEASED> not Null, then <DATEINT>; <DATEMATCH>; <FOSTERCARE>; <NBADOPTR>; <SEXADOPTR>; and <LSADOPTR> should not be provided
        mask = merged["DATEPLACEDCEASED"].notna() & (
            merged["DATEINT"].notna()
            | merged["DATEMATCH"].notna()
            | merged["FOSTERCARE"].notna()
            | merged["NBADOPTR"].notna()
            | merged["SEXADOPTR"].notna()
            | merged["LSADOPTR"].notna()
        )
        # error locations
        paerrorlocs = merged.loc[mask, "indexplaced"]
        aderrorlocs = merged.loc[mask, "indexad1"]
        # return result
        return {
            "PlacedAdoption": paerrorlocs.tolist(),
            "AD1": aderrorlocs.tolist(),
        }


def test_validate():
    import pandas as pd

    fake_placed_adoption = pd.DataFrame(
        {
            "DATE_PLACED_CEASED": [
                "08/03/2020",
                "22/06/2020",
                "13/10/2022",
                "24/10/2021",
                pd.NA,
            ],
            "CHILD": ["104", "105", "107", "108", "109"],
        }
    )
    fake_data_ad1 = pd.DataFrame(
        {
            "CHILD": ["104", "105", "107", "108", "109"],
            "DATE_INT": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "DATE_MATCH": [pd.NA, "XXX", "XXX", pd.NA, "XXX"],
            "FOSTER_CARE": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "NB_ADOPTR": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "SEX_ADOPTR": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "LS_ADOPTR": [pd.NA, pd.NA, "XXX", "XXX", "XXX"],
        }
    )

    fake_dfs = {"PlacedAdoption": fake_placed_adoption, "AD1": fake_data_ad1}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"PlacedAdoption": [1, 2, 3], "AD1": [1, 2, 3]}
