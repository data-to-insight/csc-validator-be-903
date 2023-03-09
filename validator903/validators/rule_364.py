import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="364",
        description="Sections 41-46 of Police and Criminal Evidence (PACE; 1984) severely limits "
        + "the time a child can be detained in custody in Local Authority (LA) accommodation.",
        affected_fields=["LS", "DECOM", "DEC"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        episodes = dfs["Episodes"]
        collection_end_str = dfs["metadata"]["collection_end"]

        J2_eps = episodes[episodes["LS"] == "J2"].copy()
        J2_eps["original_index"] = J2_eps.index

        J2_eps["DECOM"] = pd.to_datetime(
            J2_eps["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        J2_eps = J2_eps[J2_eps["DECOM"].notna()]
        J2_eps.loc[J2_eps["DEC"].isna(), "DEC"] = collection_end_str
        J2_eps["DEC"] = pd.to_datetime(
            J2_eps["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        J2_eps.sort_values(["CHILD", "DECOM"])

        J2_eps["index"] = pd.RangeIndex(0, len(J2_eps))
        J2_eps["index_prev"] = J2_eps["index"] + 1
        J2_eps = J2_eps.merge(
            J2_eps,
            left_on="index",
            right_on="index_prev",
            how="left",
            suffixes=[None, "_prev"],
        )
        J2_eps = J2_eps[
            ["original_index", "DECOM", "DEC", "DEC_prev", "CHILD", "CHILD_prev", "LS"]
        ]

        J2_eps["new_period"] = (J2_eps["DECOM"] > J2_eps["DEC_prev"]) | (
            J2_eps["CHILD"] != J2_eps["CHILD_prev"]
        )

        J2_eps["duration"] = (J2_eps["DEC"] - J2_eps["DECOM"]).dt.days
        J2_eps["period_id"] = J2_eps["new_period"].astype(int).cumsum()
        J2_eps["period_duration"] = J2_eps.groupby("period_id")["duration"].transform(
            sum
        )

        error_mask = J2_eps["period_duration"] > 21

        return {"Episodes": J2_eps.loc[error_mask, "original_index"].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    test_eps = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DECOM": "01/01/2000",
                "DEC": "01/01/2001",
                "LS": "J2",
            },  # 0 Fail!
            {"CHILD": 101, "DECOM": "01/01/2001", "DEC": "20/12/2001", "LS": "X"},  # 1
            {
                "CHILD": 101,
                "DECOM": "20/12/2001",
                "DEC": "12/01/2002",
                "LS": "J2",
            },  # 2 Fail!
            {
                "CHILD": 2002,
                "DECOM": "01/01/2000",
                "DEC": "10/01/2000",
                "LS": "J2",
            },  # 3 ^ Fa
            {
                "CHILD": 2002,
                "DECOM": "10/01/2000",
                "DEC": "23/01/2001",
                "LS": "J2",
            },  # 4 v il!
            {
                "CHILD": 2002,
                "DECOM": "01/01/2002",
                "DEC": "10/01/2002",
                "LS": "J2",
            },  # 5
            {"CHILD": 2002, "DECOM": "10/01/2002", "DEC": "11/01/2002", "LS": "X"},  # 6
            {
                "CHILD": 2002,
                "DECOM": "11/01/2002",
                "DEC": "25/01/2002",
                "LS": "J2",
            },  # 7
            {
                "CHILD": 30003,
                "DECOM": "25/01/2002",
                "DEC": "10/03/2001",
                "LS": "J2",
            },  # 8 DEC < DECOM
            {
                "CHILD": 30003,
                "DECOM": "25/01/2002",
                "DEC": pd.NA,
                "LS": "J2",
            },  # 9 Fail!
            {
                "CHILD": 30003,
                "DECOM": pd.NA,
                "DEC": "25/01/2002",
                "LS": "J2",
            },  # 10 decom.isNA
            {"CHILD": 30003, "DECOM": pd.NA, "DEC": pd.NA, "LS": "J2"},  # 11
        ]
    )

    test_meta = {"collection_end": "01/04/2002"}

    test_dfs = {"Episodes": test_eps, "metadata": test_meta}

    error_defn, error_func = validate()

    result = error_func(test_dfs)

    assert result == {"Episodes": [0, 2, 3, 4, 9]}
