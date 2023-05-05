import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="367",
    message="The maximum amount of respite care allowable is 75 days in any 12-month period.",
    affected_fields=["LS", "DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    V3eps = episodes[episodes["LS"] == "V3"]

    V3eps = V3eps.dropna(
        subset=["DECOM"]
    )  # missing DECOM should get fixed before looking for this error

    collectionstart = pd.todatetime(
        dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
    )
    collectionend = pd.todatetime(
        dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
    )
    V3eps["DECOMdt"] = pd.todatetime(V3eps["DECOM"], format="%d/%m/%Y", errors="coerce")
    V3eps["DECdt"] = pd.todatetime(V3eps["DEC"], format="%d/%m/%Y", errors="coerce")

    # truncate episode start/end dates to collection start/end respectively
    V3eps.loc[
        V3eps["DEC"].isna() | (V3eps["DECdt"] > collectionend), "DECdt"
    ] = collectionend
    V3eps.loc[V3eps["DECOMdt"] < collectionstart, "DECOMdt"] = collectionstart

    V3eps["duration"] = (V3eps["DECdt"] - V3eps["DECOMdt"]).dt.days
    V3eps = V3eps[V3eps["duration"] > 0]

    V3eps["yeartotalduration"] = V3eps.groupby("CHILD")["duration"].transform(sum)

    errormask = V3eps["yeartotalduration"] > 75

    return {"Episodes": V3eps.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    test_eps = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DECOM": "01/01/2000",
                "DEC": "01/06/2000",
                "LS": "V3",
            },  # 0 decom-->col_start
            {
                "CHILD": 2002,
                "DECOM": "01/01/2000",
                "DEC": "01/05/2000",
                "LS": "V3",
            },  # 1 decom-->col_start
            {
                "CHILD": 30003,
                "DECOM": "01/04/2000",
                "DEC": "01/05/2000",
                "LS": "V3",
            },  # 2 ^ Fail!
            {
                "CHILD": 30003,
                "DECOM": "01/05/2000",
                "DEC": "01/07/2000",
                "LS": "xx",
            },  # 3 |
            {
                "CHILD": 30003,
                "DECOM": "01/06/2000",
                "DEC": "01/07/2000",
                "LS": "V3",
            },  # 4 | Fail!
            {
                "CHILD": 30003,
                "DECOM": "01/07/2000",
                "DEC": "01/08/2000",
                "LS": "V3",
            },  # 5 v Fail!
            {
                "CHILD": 400004,
                "DECOM": "01/08/2000",
                "DEC": "01/07/2000",
                "LS": "V3",
            },  # 6
            {
                "CHILD": 400004,
                "DECOM": "01/08/2000",
                "DEC": "01/11/2000",
                "LS": "V3",
            },  # 7 Fail!
            {"CHILD": 555, "DECOM": "01/07/2000", "DEC": pd.NA, "LS": "V3"},  # 8 Fail!
        ]
    )

    test_meta = {"collection_start": "01/04/2000", "collection_end": "01/04/2001"}

    test_dfs = {"Episodes": test_eps, "metadata": test_meta}

    error_defn, error_func = validate()

    result = error_func(test_dfs)

    assert result == {"Episodes": [2, 4, 5, 7, 8]}
