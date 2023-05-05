import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="364",
    message="Sections 41-46 of Police and Criminal Evidence (PACE; 1984) severely limits "
    + "the time a child can be detained in custody in Local Authority (LA) accommodation.",
    affected_fields=["LS", "DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    episodes = dfs["Episodes"]
    collectionendstr = dfs["metadata"]["collectionend"]

    J2eps = episodes[episodes["LS"] == "J2"].copy()
    J2eps["originalindex"] = J2eps.index

    J2eps["DECOM"] = pd.todatetime(J2eps["DECOM"], format="%d/%m/%Y", errors="coerce")
    J2eps = J2eps[J2eps["DECOM"].notna()]
    J2eps.loc[J2eps["DEC"].isna(), "DEC"] = collectionendstr
    J2eps["DEC"] = pd.todatetime(J2eps["DEC"], format="%d/%m/%Y", errors="coerce")

    J2eps.sortvalues(["CHILD", "DECOM"])

    J2eps["index"] = pd.RangeIndex(0, len(J2eps))
    J2eps["indexprev"] = J2eps["index"] + 1
    J2eps = J2eps.merge(
        J2eps,
        lefton="index",
        righton="indexprev",
        how="left",
        suffixes=[None, "prev"],
    )
    J2eps = J2eps[
        ["originalindex", "DECOM", "DEC", "DECprev", "CHILD", "CHILDprev", "LS"]
    ]

    J2eps["newperiod"] = (J2eps["DECOM"] > J2eps["DECprev"]) | (
        J2eps["CHILD"] != J2eps["CHILDprev"]
    )

    J2eps["duration"] = (J2eps["DEC"] - J2eps["DECOM"]).dt.days
    J2eps["periodid"] = J2eps["newperiod"].astype(int).cumsum()
    J2eps["periodduration"] = J2eps.groupby("periodid")["duration"].transform(sum)

    errormask = J2eps["periodduration"] > 21

    return {"Episodes": J2eps.loc[errormask, "originalindex"].tolist()}


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
