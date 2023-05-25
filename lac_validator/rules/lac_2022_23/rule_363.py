import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="363",
    message="Child assessment order (CAO) lasted longer than 7 days allowed in the Children Act 1989.",
    affected_fields=["LS", "DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    episodes = dfs["Episodes"]
    collection_end_str = dfs["metadata"]["collection_end"]

    L2_eps = episodes[episodes["LS"] == "L3"].copy()
    L2_eps["original_index"] = L2_eps.index
    L2_eps = L2_eps[L2_eps["DECOM"].notna()]

    L2_eps.loc[L2_eps["DEC"].isna(), "DEC"] = collection_end_str
    L2_eps["DECOM"] = pd.to_datetime(
        L2_eps["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    L2_eps = L2_eps.dropna(subset=["DECOM"])
    L2_eps["DEC"] = pd.to_datetime(L2_eps["DEC"], format="%d/%m/%Y", errors="coerce")

    L2_eps.sort_values(["CHILD", "DECOM"])

    L2_eps["index"] = pd.RangeIndex(0, len(L2_eps))
    L2_eps["index+1"] = L2_eps["index"] + 1
    L2_eps = L2_eps.merge(
        L2_eps,
        left_on="index",
        right_on="index+1",
        how="left",
        suffixes=[None, "_prev"],
    )
    L2_eps = L2_eps[
        ["original_index", "DECOM", "DEC", "DEC_prev", "CHILD", "CHILD_prev", "LS"]
    ]

    L2_eps["new_period"] = (L2_eps["DECOM"] > L2_eps["DEC_prev"]) | (
        L2_eps["CHILD"] != L2_eps["CHILD_prev"]
    )

    L2_eps["duration"] = (L2_eps["DEC"] - L2_eps["DECOM"]).dt.days
    L2_eps["period_id"] = L2_eps["new_period"].astype(int).cumsum()
    L2_eps["period_duration"] = L2_eps.groupby("period_id")["duration"].transform(sum)

    error_mask = L2_eps["period_duration"] > 7

    return {"Episodes": L2_eps.loc[error_mask, "original_index"].to_list()}


def test_validate():
    import pandas as pd

    test_eps = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DECOM": "01/01/2000",
                "DEC": "01/01/2001",
                "LS": "L3",
            },  # 0 Fail!
            {"CHILD": 101, "DECOM": "01/01/2001", "DEC": "20/12/2001", "LS": "X"},  # 1
            {
                "CHILD": 101,
                "DECOM": "20/12/2001",
                "DEC": "12/01/2002",
                "LS": "L3",
            },  # 2 Fail!
            {
                "CHILD": 2002,
                "DECOM": "01/01/2000",
                "DEC": "03/01/2000",
                "LS": "L3",
            },  # 3 ^ Fa
            {
                "CHILD": 2002,
                "DECOM": "03/01/2000",
                "DEC": "09/01/2001",
                "LS": "L3",
            },  # 4 v il!
            {
                "CHILD": 2002,
                "DECOM": "01/01/2002",
                "DEC": "07/01/2002",
                "LS": "L3",
            },  # 5
            {"CHILD": 2002, "DECOM": "10/01/2002", "DEC": "11/01/2002", "LS": "X"},  # 6
            {
                "CHILD": 2002,
                "DECOM": "11/01/2002",
                "DEC": "17/01/2002",
                "LS": "L3",
            },  # 7
            {
                "CHILD": 30003,
                "DECOM": "25/01/2002",
                "DEC": "10/03/2001",
                "LS": "L3",
            },  # 8 (decom>dec)
            {
                "CHILD": 30003,
                "DECOM": "25/01/2002",
                "DEC": pd.NA,
                "LS": "L3",
            },  # 9 Fail!
            {
                "CHILD": 30003,
                "DECOM": pd.NA,
                "DEC": "25/01/2002",
                "LS": "L3",
            },  # 10 decom.isNA
            {"CHILD": 30003, "DECOM": pd.NA, "DEC": pd.NA, "LS": "L3"},  # 11
        ]
    )

    test_meta = {"collection_end": "01/04/2002"}

    test_dfs = {"Episodes": test_eps, "metadata": test_meta}

    

    result = error_func(test_dfs)

    assert result == {"Episodes": [0, 2, 3, 4, 9]}
