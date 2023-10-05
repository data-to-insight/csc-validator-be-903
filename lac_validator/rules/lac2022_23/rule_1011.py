import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1011",
    message="This child is recorded as having his/her care transferred to another local authority for the final episode and therefore should not have the care leaver information completed.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "OC3" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        oc3 = dfs["OC3"]
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")

        # If final <REC> = 'E3' then <IN_TOUCH>; <ACTIV> and <ACCOM> should not be provided
        epi.sort_values(["CHILD", "DECOM"], inplace=True)
        grouped_decom_by_child = epi.groupby(["CHILD"])["DECOM"].idxmax(skipna=True)
        max_decom_only = epi.loc[epi.index.isin(grouped_decom_by_child), :]
        E3_is_last = max_decom_only[max_decom_only["REC"] == "E3"]

        oc3.reset_index(inplace=True)
        cohort_to_check = oc3.merge(E3_is_last, on="CHILD", how="inner")
        error_mask = cohort_to_check[["IN_TOUCH", "ACTIV", "ACCOM"]].notna().any(axis=1)

        error_list = cohort_to_check["index"][error_mask].to_list()
        error_list = list(set(error_list))
        error_list.sort()

        return {"OC3": error_list}


def test_validate():
    import pandas as pd

    fake_data_epi = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "01/06/2020", "REC": "E3"},  # 0
            {"CHILD": "111", "DECOM": "05/06/2020", "REC": "E11"},  # 1
            {"CHILD": "111", "DECOM": "06/06/2020", "REC": "E3"},  # 2  Max E3
            {"CHILD": "123", "DECOM": "08/06/2020", "REC": "X1"},  # 3
            {"CHILD": "222", "DECOM": "05/06/2020", "REC": "E3"},  # 4   Max E3
            {"CHILD": "333", "DECOM": "06/06/2020", "REC": "X1"},  # 5
            {"CHILD": "333", "DECOM": "07/06/2020", "REC": "E3"},  # 6  Max E3
            {"CHILD": "444", "DECOM": "08/06/2020", "REC": "E3"},  # 7
            {"CHILD": "444", "DECOM": "09/06/2020", "REC": "E3"},  # 8
            {"CHILD": "444", "DECOM": "15/06/2020", "REC": "X1"},  # 9
            {"CHILD": "555", "DECOM": "15/06/2020", "REC": "E3"},  # 10  Max E3
            {"CHILD": "666", "DECOM": "15/06/2020", "REC": pd.NA},  # 11
        ]
    )
    fake_data_oc3 = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "IN_TOUCH": "Whatever",
                "ACTIV": pd.NA,
                "ACCOM": "Whatever",
            },  # 0 Fails
            {
                "CHILD": "222",
                "IN_TOUCH": pd.NA,
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },  # 1 All null values so will pass
            {
                "CHILD": "333",
                "IN_TOUCH": "Whatever",
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },  # 2 Fails
            {
                "CHILD": "777",
                "IN_TOUCH": "Whatever",
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },  # 3
            {
                "CHILD": "555",
                "IN_TOUCH": "Whatever",
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },  # 4 Fails
        ]
    )
    fake_dfs = {"OC3": fake_data_oc3, "Episodes": fake_data_epi}

    result = validate(fake_dfs)

    assert result == {"OC3": [0, 2, 4]}
