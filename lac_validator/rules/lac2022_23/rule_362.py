import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="362",
    message="Emergency protection order (EPO) lasted longer than 21 days",
    affected_fields=["DECOM", "LS", "DEC"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]

        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        collection_end = pd.to_datetime(
            dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
        )

        epi.sort_values(["CHILD", "DECOM"], inplace=True)
        epi.reset_index(inplace=True)
        epi.reset_index(inplace=True)

        epi["LAG"] = epi["level_0"] - 1

        epi["DEC"].fillna(collection_end, inplace=True)

        err_co = epi.merge(
            epi,
            how="left",
            left_on="level_0",
            right_on="LAG",
            suffixes=["", "_NEXT"],
        ).query("LS == 'L2'")

        # Create a partition "FLOWS" for two or more separate flow sequences of L2 code dates within the same child.
        # when the dec / decom_next dates stop flowing or the child id changes
        # the cumsum is incremented this can then be used as the partition.
        err_co["FLOWS"] = (err_co["DEC"] == err_co["DECOM_NEXT"]) & (
            err_co["CHILD"] == err_co["CHILD_NEXT"]
        )
        err_co["FLOWS"] = err_co["FLOWS"].shift(1)
        err_co["FLOWS"].fillna(False, inplace=True)
        err_co["FLOWS"] = ~err_co["FLOWS"]
        err_co["FLOWS"] = err_co["FLOWS"].astype(int).cumsum()

        # Calc the min decom and max dec in each group so the days between them can be calculated.
        grp_decom = (
            err_co.groupby(["CHILD", "FLOWS"])["DECOM"]
            .min()
            .to_frame(name="MIN_DECOM")
            .reset_index()
        )
        grp_dec = (
            err_co.groupby(["CHILD", "FLOWS"])["DEC"]
            .max()
            .to_frame(name="MAX_DEC")
            .reset_index()
        )
        grp_len_l2 = grp_decom.merge(grp_dec, how="inner", on=["CHILD", "FLOWS"])

        # Throw out anything <= 21 days.
        grp_len_l2["DAY_DIF"] = (
            grp_len_l2["MAX_DEC"] - grp_len_l2["MIN_DECOM"]
        ).dt.days
        grp_len_l2 = grp_len_l2.query("DAY_DIF > 21").copy()

        # Inner join back to the err_co and get the original index out.
        err_co["MERGE_KEY"] = err_co["CHILD"].astype(str) + err_co["FLOWS"].astype(str)
        grp_len_l2["MERGE_KEY"] = grp_len_l2["CHILD"].astype(str) + grp_len_l2[
            "FLOWS"
        ].astype(str)
        err_final = err_co.merge(
            grp_len_l2, how="inner", on=["MERGE_KEY"], suffixes=["", "_IG"]
        )

        err_list = err_final["index"].unique().tolist()
        err_list.sort()

        return {"Episodes": err_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
                "LS": "L2",
            },  # 0  CHANGE |a
            {
                "CHILD": "111",
                "DECOM": "04/06/2020",
                "DEC": "05/06/2020",
                "LS": "L2",
            },  # 1         |a Passes as <=21
            {
                "CHILD": "111",
                "DECOM": "06/07/2020",
                "DEC": "07/07/2020",
                "LS": "E2",
            },  # 2
            {
                "CHILD": "111",
                "DECOM": "08/09/2020",
                "DEC": "09/10/2020",
                "LS": "L2",
            },  # 3  CHANGE |b  Fail
            {
                "CHILD": "111",
                "DECOM": "09/10/2020",
                "DEC": "12/11/2020",
                "LS": "L2",
            },  # 4         |b  Fail
            {
                "CHILD": "333",
                "DECOM": "06/06/2020",
                "DEC": "10/06/2020",
                "LS": "L2",
            },  # 5  CHANGE |c  Fail
            {
                "CHILD": "333",
                "DECOM": "10/06/2020",
                "DEC": "12/10/2020",
                "LS": "L2",
            },  # 6         |c  Fail
            {
                "CHILD": "444",
                "DECOM": "07/06/2020",
                "DEC": "08/07/2020",
                "LS": "L2",
            },  # 7  CHANGE |d  Fail
            {
                "CHILD": "444",
                "DECOM": "08/08/2020",
                "DEC": "09/08/2020",
                "LS": "E4",
            },  # 8
            {
                "CHILD": "444",
                "DECOM": "09/08/2020",
                "DEC": "15/08/2020",
                "LS": "L2",
            },  # 9  CHANGE |e  Fail
            {
                "CHILD": "444",
                "DECOM": "15/08/2020",
                "DEC": pd.NA,
                "LS": "L2",
            },  # 10        |e  Fail
            {
                "CHILD": "555",
                "DECOM": "15/03/2021",
                "DEC": pd.NA,
                "LS": "L2",
            },  # 11 CHANGE |f  Passes as <=21
        ]
    )
    metadata = {"collection_end": "31/03/2021"}

    fake_dfs = {"Episodes": fake_data, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Episodes": [3, 4, 5, 6, 7, 9, 10]}
