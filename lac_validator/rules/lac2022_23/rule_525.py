import pandas as pd

from lac_validator.rule_engine import rule_definition


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
    tables=["PlacedAdoption", "AD1"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs or "AD1" not in dfs:
        return {}
    else:
        placed_adoption = dfs["PlacedAdoption"]
        ad1 = dfs["AD1"]
        # prepare to merge
        placed_adoption.reset_index(inplace=True)
        ad1.reset_index(inplace=True)

        merged = placed_adoption.merge(
            ad1, on="CHILD", how="left", suffixes=["_placed", "_ad1"]
        )
        # If <DATE_PLACED_CEASED> not Null, then <DATE_INT>; <DATE_MATCH>; <FOSTER_CARE>; <NB_ADOPTR>; <SEX_ADOPTR>; and <LS_ADOPTR> should not be provided
        mask = merged["DATE_PLACED_CEASED"].notna() & (
            merged["DATE_INT"].notna()
            | merged["DATE_MATCH"].notna()
            | merged["FOSTER_CARE"].notna()
            | merged["NB_ADOPTR"].notna()
            | merged["SEX_ADOPTR"].notna()
            | merged["LS_ADOPTR"].notna()
        )
        # error locations
        pa_error_locs = merged.loc[mask, "index_placed"]
        ad_error_locs = merged.loc[mask, "index_ad1"]
        # return result
        return {
            "PlacedAdoption": pa_error_locs.tolist(),
            "AD1": ad_error_locs.tolist(),
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

    result = validate(fake_dfs)
    assert result == {"PlacedAdoption": [1, 2, 3], "AD1": [1, 2, 3]}
