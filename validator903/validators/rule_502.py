import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="502",
        description="Last year's record ended with an open episode. The date on which that episode started does not match the start date of the first episode on this year’s record.",
        affected_fields=["DECOM"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "Episodes_last" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            epi_last = dfs["Episodes_last"]
            epi = epi.reset_index()

            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epi_last["DECOM"] = pd.to_datetime(
                epi_last["DECOM"], format="%d/%m/%Y", errors="coerce"
            )

            epi_last_no_dec = epi_last[epi_last["DEC"].isna()]

            epi_min_decoms_index = (
                epi[["CHILD", "DECOM"]].groupby(["CHILD"])["DECOM"].idxmin()
            )

            epi_min_decom_df = epi.loc[epi_min_decoms_index, :]

            merged_episodes = epi_min_decom_df.merge(
                epi_last_no_dec, on="CHILD", how="inner"
            )
            error_cohort = merged_episodes[
                merged_episodes["DECOM_x"] != merged_episodes["DECOM_y"]
            ]

            error_list = error_cohort["index"].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {"Episodes": error_list}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "01/06/2020"},  # 0  Min   Fails
            {"CHILD": "111", "DECOM": "05/06/2020"},  # 1
            {"CHILD": "111", "DECOM": "06/06/2020"},  # 2
            {"CHILD": "123", "DECOM": "08/06/2020"},  # 3  Min
            {"CHILD": "222", "DECOM": "05/06/2020"},  # 4   Min   Fails
            {"CHILD": "333", "DECOM": "06/06/2020"},  # 5  Min
            {"CHILD": "333", "DECOM": "07/06/2020"},  # 6
            {"CHILD": "444", "DECOM": "08/06/2020"},  # 7  Min   Fails
            {"CHILD": "444", "DECOM": "09/06/2020"},  # 8
            {"CHILD": "444", "DECOM": "15/06/2020"},  # 9
            {"CHILD": "555", "DECOM": "15/06/2020"},  # 10
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "05/06/2020", "DEC": pd.NA},
            {"CHILD": "123", "DECOM": "08/06/2020", "DEC": pd.NA},
            {"CHILD": "222", "DECOM": "09/06/2020", "DEC": pd.NA},
            {"CHILD": "333", "DECOM": "06/06/2020", "DEC": "05/06/2020"},
            {"CHILD": "333", "DECOM": "07/06/2020", "DEC": "05/06/2020"},
            {"CHILD": "444", "DECOM": "08/06/2020", "DEC": "05/06/2020"},
            {"CHILD": "444", "DECOM": "09/06/2020", "DEC": "05/06/2020"},
            {"CHILD": "444", "DECOM": "19/06/2020", "DEC": pd.NA},
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 4, 7]}
