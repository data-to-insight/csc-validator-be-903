import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="630",
    message="Information on previous permanence option should be returned.",
    affected_fields=["RNE"],
)
def validate(dfs):
    if "PrevPerm" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        pre = dfs["PrevPerm"]

        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        collectionstart = pd.todatetime(
            dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
        )

        epi = epi.resetindex()

        # Form the episode dataframe which has an 'RNE' of 'S' in this financial year
        epihasrneofSinyear = epi[
            (epi["RNE"] == "S") & (epi["DECOM"] >= collectionstart)
        ]
        # Merge to see
        # 1) which CHILD ids are missing from the PrevPerm file
        # 2) which CHILD are in the prevPerm file, but don't have the LAPERM/DATEPERM field completed where they should be
        # 3) which CHILD are in the PrevPerm file, but don't have the PREVPERM field completed.
        mergedepipreperm = epihasrneofSinyear.merge(
            pre, on="CHILD", how="left", indicator=True
        )

        errornotinpreperm = mergedepipreperm["merge"] == "leftonly"
        errorwrongvaluesinpreperm = (mergedepipreperm["PREVPERM"] != "Z1") & (
            mergedepipreperm[["LAPERM", "DATEPERM"]].isna().any(axis=1)
        )
        errornullprevperm = (mergedepipreperm["merge"] == "both") & (
            mergedepipreperm["PREVPERM"].isna()
        )

        errormask = errornotinpreperm | errorwrongvaluesinpreperm | errornullprevperm

        errorlist = mergedepipreperm[errormask]["index"].tolist()
        errorlist = list(set(errorlist))
        errorlist.sort()

        return {"Episodes": errorlist}


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            "DECOM": [
                "01/04/2021",
                "01/04/2021",
                "01/04/2021",
                "01/04/2021",
                "31/03/2021",
                "01/04/2021",
                "01/04/2021",
                "01/04/2021",
                "01/04/2021",
            ],
            # 4 will now pass, it's before this year
            "RNE": ["T", "S", "S", "P", "S", "S", "S", "S", "S"],
        }
    )
    fake_pre = pd.DataFrame(
        {
            "CHILD": ["2", "4", "5", "6", "7", "8"],
            "PREV_PERM": ["Z1", "P1", "P1", "Z1", pd.NA, "P1"],
            "LA_PERM": [pd.NA, "352", pd.NA, pd.NA, pd.NA, "352"],
            "DATE_PERM": [pd.NA, pd.NA, "01/05/2000", pd.NA, pd.NA, "05/05/2020"],
        }
    )
    metadata = {"collection_start": "01/04/2021"}

    fake_dfs = {"Episodes": fake_epi, "PrevPerm": fake_pre, "metadata": metadata}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Episodes": [1, 5, 7]}
