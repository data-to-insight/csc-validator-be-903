import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="630",
        description="Information on previous permanence option should be returned.",
        affected_fields=["RNE"],
    )

    def _validate(dfs):
        if "PrevPerm" not in dfs or "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            pre = dfs["PrevPerm"]

            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            collection_start = pd.to_datetime(
                dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
            )

            epi = epi.reset_index()

            # Form the episode dataframe which has an 'RNE' of 'S' in this financial year
            epi_has_rne_of_S_in_year = epi[
                (epi["RNE"] == "S") & (epi["DECOM"] >= collection_start)
            ]
            # Merge to see
            # 1) which CHILD ids are missing from the PrevPerm file
            # 2) which CHILD are in the prevPerm file, but don't have the LA_PERM/DATE_PERM field completed where they should be
            # 3) which CHILD are in the PrevPerm file, but don't have the PREV_PERM field completed.
            merged_epi_preperm = epi_has_rne_of_S_in_year.merge(
                pre, on="CHILD", how="left", indicator=True
            )

            error_not_in_preperm = merged_epi_preperm["_merge"] == "left_only"
            error_wrong_values_in_preperm = (
                merged_epi_preperm["PREV_PERM"] != "Z1"
            ) & (merged_epi_preperm[["LA_PERM", "DATE_PERM"]].isna().any(axis=1))
            error_null_prev_perm = (merged_epi_preperm["_merge"] == "both") & (
                merged_epi_preperm["PREV_PERM"].isna()
            )

            error_mask = (
                error_not_in_preperm
                | error_wrong_values_in_preperm
                | error_null_prev_perm
            )

            error_list = merged_epi_preperm[error_mask]["index"].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {"Episodes": error_list}

    return error, _validate


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
