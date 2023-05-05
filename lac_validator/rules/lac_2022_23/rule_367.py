import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="367",
    message="The maximum amount of respite care allowable is 75 days in any 12-month period.",
    affected_fields=["LS", "DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    V3_eps = episodes[episodes["LS"] == "V3"]

    V3_eps = V3_eps.dropna(
        subset=["DECOM"]
    )  # missing DECOM should get fixed before looking for this error

    collection_start = pd.to_datetime(
        dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
    )
    collection_end = pd.to_datetime(
        dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
    )
    V3_eps["DECOM_dt"] = pd.to_datetime(
        V3_eps["DECOM"], format="%d/%m/%Y", errors="coerce"
    )
    V3_eps["DEC_dt"] = pd.to_datetime(V3_eps["DEC"], format="%d/%m/%Y", errors="coerce")

    # truncate episode start/end dates to collection start/end respectively
    V3_eps.loc[
        V3_eps["DEC"].isna() | (V3_eps["DEC_dt"] > collection_end), "DEC_dt"
    ] = collection_end
    V3_eps.loc[V3_eps["DECOM_dt"] < collection_start, "DECOM_dt"] = collection_start

    V3_eps["duration"] = (V3_eps["DEC_dt"] - V3_eps["DECOM_dt"]).dt.days
    V3_eps = V3_eps[V3_eps["duration"] > 0]

    V3_eps["year_total_duration"] = V3_eps.groupby("CHILD")["duration"].transform(sum)

    error_mask = V3_eps["year_total_duration"] > 75

    return {"Episodes": V3_eps.index[error_mask].to_list()}


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
