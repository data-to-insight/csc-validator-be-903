import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="562",
        description="Episode commenced before the start of the current collection year but there is a missing continuous episode in the previous year.",
        affected_fields=["DECOM"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "Episodes_last" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            epi_last = dfs["Episodes_last"]
            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            epi_last["DECOM"] = pd.to_datetime(
                epi_last["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            collection_start = pd.to_datetime(
                dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
            )

            epi.reset_index(inplace=True)
            epi = epi[epi["DECOM"] < collection_start]

            grp_decom_by_child = epi.groupby(["CHILD"])["DECOM"].idxmin(skipna=True)
            min_decom = epi.loc[epi.index.isin(grp_decom_by_child), :]

            grp_last_decom_by_child = epi_last.groupby(["CHILD"])["DECOM"].idxmax(
                skipna=True
            )
            max_last_decom = epi_last.loc[
                epi_last.index.isin(grp_last_decom_by_child), :
            ]

            merged_co = min_decom.merge(
                max_last_decom,
                how="left",
                on=["CHILD", "DECOM"],
                suffixes=["", "_PRE"],
                indicator=True,
            )
            error_cohort = merged_co[merged_co["_merge"] == "left_only"]

            error_list = error_cohort["index"].to_list()
            error_list = list(set(error_list))
            error_list.sort()
            return {"Episodes": error_list}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "15/03/2021"},  # 0 Min pre year start
            {"CHILD": "111", "DECOM": "05/06/2021"},  # 1
            {"CHILD": "222", "DECOM": "13/03/2021"},  # 2 Min pre year start
            {"CHILD": "222", "DECOM": "08/06/2021"},  # 3
            {"CHILD": "222", "DECOM": "05/06/2021"},  # 4
            {"CHILD": "333", "DECOM": "01/01/2021"},  # 5 Min pre year start
            {"CHILD": "444", "DECOM": "01/05/2021"},  # 6
        ]
    )
    fake_last = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "01/06/2020"},  # 0
            {"CHILD": "111", "DECOM": "05/06/2020"},  # 1
            {"CHILD": "111", "DECOM": "15/03/2021"},  # 2 Max matches next year
            {"CHILD": "222", "DECOM": "01/02/2021"},  # 3
            {"CHILD": "222", "DECOM": "11/03/2021"},  # 4 Max doesn't match - fail
            {"CHILD": "333", "DECOM": "06/06/2020"},  # 5 Max doesn't match - fail
        ]
    )
    metadata = {"collection_start": "01/04/2021"}

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_last, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 5]}
