from validator903.types import ErrorDefinition


@rule_definition(
    code="335",
    message="The current foster value (0) suggests that child is not adopted by current foster carer, but last placement is A2, A3, or A5. Or the current foster value (1) suggests that child is adopted by current foster carer, but last placement is A1, A4 or A6.",
    affected_fields=["PLACE", "FOSTER_CARE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "AD1" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        ad1 = dfs["AD1"]

        # prepare to merge
        episodes.resetindex(inplace=True)
        ad1.resetindex(inplace=True)
        merged = episodes.merge(ad1, on="CHILD", how="left", suffixes=["eps", "ad1"])

        # Where <PL> = 'A2', 'A3' or 'A5' and <DEC> = 'E1', 'E11', 'E12' <FOSTERCARE> should not be '0'; Where <PL> = ‘A1’, ‘A4’ or ‘A6’ and <REC> = ‘E1’, ‘E11’, ‘E12’ <FOSTERCARE> should not be ‘1’.
        mask = merged["REC"].isin(["E1", "E11", "E12"]) & (
            (
                merged["PLACE"].isin(["A2", "A3", "A5"])
                & (merged["FOSTERCARE"].astype(str) == "0")
            )
            | (
                merged["PLACE"].isin(["A1", "A4", "A6"])
                & (merged["FOSTERCARE"].astype(str) == "1")
            )
        )
        epserrorlocs = merged.loc[mask, "indexeps"]
        ad1errorlocs = merged.loc[mask, "indexad1"]

        # use .unique since join is many to one
        return {
            "Episodes": epserrorlocs.tolist(),
            "AD1": ad1errorlocs.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        {
            "PLACE": ["A2", "--", "A1", "--", "A4", "--", "A5", "A3"],
            "REC": ["E1", "E1", "E1", "E12", "E11", "E1", "--", "E12"],
            "CHILD": ["10", "11", "12", "13", "14", "15", "16", "17"],
        }
    )
    fake_data_ad1 = pd.DataFrame(
        {
            "FOSTER_CARE": [0, 1, "0", "1", 2, "former foster carer", "", pd.NA],
            "CHILD": ["10", "11", "12", "13", "14", "15", "16", "17"],
        }
    )
    fake_dfs = {"Episodes": fake_data_eps, "AD1": fake_data_ad1}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0], "AD1": [0]}
