import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="357",
    message="If this is the first episode ever for this child, reason for new episode must be S.  "
    "Check whether there is an episode immediately preceding this one, which has been left out.  "
    "If not the reason for new episode code must be amended to S.",
    affected_fields=["RNE"],
)

# !# Potential false negatives for first episodes before the current collection year?
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    eps = dfs["Episodes"]
    collectionstart = pd.todatetime(
        dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
    )
    eps["DECOM"] = pd.todatetime(eps["DECOM"], format="%d/%m/%Y", errors="coerce")

    eps = eps.loc[eps["DECOM"].notnull()]

    firsteps = eps.loc[eps.groupby("CHILD")["DECOM"].idxmin()].loc[
        eps["DECOM"] >= collectionstart
    ]

    errs = firsteps[firsteps["RNE"] != "S"].index.tolist()

    return {"Episodes": errs}


def test_validate():
    import pandas as pd

    episodes = pd.DataFrame(
        [
            {"CHILD": "000", "DECOM": "01/01/2001", "RNE": "!!"},
            {"CHILD": "111", "DECOM": "11/11/2011", "RNE": "ok"},
            {"CHILD": "111", "DECOM": "01/01/2000", "RNE": "S"},
            {"CHILD": "222", "DECOM": "11/11/2011", "RNE": "ok"},
            {"CHILD": "222", "DECOM": pd.NA, "RNE": "ok"},
            {"CHILD": "222", "DECOM": "01/01/2001", "RNE": "S"},
            {"CHILD": "333", "DECOM": "12/12/2012", "RNE": "ok"},
            {"CHILD": "333", "DECOM": "01/01/2001", "RNE": "!!"},
            {"CHILD": "333", "DECOM": "05/05/2005", "RNE": "ok"},
            {"CHILD": "444", "DECOM": "05/05/2005", "RNE": pd.NA},  # !!
            {
                "CHILD": "555",
                "DECOM": "01/01/1990",
                "RNE": "ok",
            },  # ok - before collection_start
        ]
    )
    metadata = {"collection_start": "31/03/1995"}
    test_dfs = {"Episodes": episodes, "metadata": metadata}

    error_defn, error_func = validate()

    test_result = error_func(test_dfs)

    assert test_result == {"Episodes": [0, 7, 9]}
