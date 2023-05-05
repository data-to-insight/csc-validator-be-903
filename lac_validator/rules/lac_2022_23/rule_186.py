import pandas as pd

from validator903.types import ErrorDefinition
from validator903.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,
)  # Check 'Episodes' present before use!


@rule_definition(
    code="186",
    message="Children aged 4 or over at the start of the year and children aged under 17 at the "
    + "end of the year and who have been looked after for at least 12 months continuously "
    + "should have a Strengths and Difficulties (SDQ) score completed.",
    affected_fields=["SDQ_SCORE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "OC2" not in dfs:
        return {}

    oc2 = dfs["OC2"]

    collectionstartstr = dfs["metadata"]["collectionstart"]
    collectionendstr = dfs["metadata"]["collectionend"]

    collectionstart = pd.todatetime(
        collectionstartstr, format="%d/%m/%Y", errors="coerce"
    )
    collectionend = pd.todatetime(collectionendstr, format="%d/%m/%Y", errors="coerce")
    oc2["DOBdt"] = pd.todatetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")

    oc2 = addCLAcolumn(dfs, "OC2")

    oc2["4thbday"] = oc2["DOBdt"] + pd.DateOffset(years=4)
    oc2["17thbday"] = oc2["DOBdt"] + pd.DateOffset(years=17)
    errormask = (
        (oc2["4thbday"] <= collectionstart)
        & (oc2["17thbday"] > collectionend)
        & oc2["CONTINUOUSLYLOOKEDAFTER"]
        & oc2[["SDQSCORE", "SDQREASON"]].isna().any(axis=1)
    )

    oc2errors = oc2.loc[errormask].index.tolist()

    return {"OC2": oc2errors}


def test_validate():
    import pandas as pd

    metadata = {"collection_start": "01/04/1980", "collection_end": "31/03/1981"}

    eps = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "DECOM": "01/03/1980",
                "DEC": "31/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "2",
                "DECOM": "01/03/1980",
                "DEC": "30/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "3",
                "DECOM": "01/03/1980",
                "DEC": "01/01/1981",
                "LS": "V3",
                "REC": "X1",
                "RNE": "o",
            },  # False
            {
                "CHILD": "4",
                "DECOM": "01/02/1970",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },
            {
                "CHILD": "5555",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "5555",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },
            {
                "CHILD": "6",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },  # !! - False
            {
                "CHILD": "6",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },  # False
            {
                "CHILD": "7777",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # False
            {
                "CHILD": "7777",
                "DECOM": "01/01/1981",
                "DEC": "01/07/1981",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },  # !! - False
            {
                "CHILD": "8",
                "DECOM": "01/01/1981",
                "DEC": "31/03/1999",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },  # False
        ]
    )

    oc2 = pd.DataFrame(
        {
            "CHILD": ["999999", "1", "2", "3", "9999", "8", "5555", "789"],
            "DOB": [
                "01/01/1974",
                "01/04/1976",
                "01/01/1978",
                "01/01/1974",
                "01/01/1974",
                "01/01/1974",
                "01/01/1955",
                "01/04/1976",
            ],
            "SDQ_SCORE": ["OO", pd.NA, "OO", "OO", pd.NA, pd.NA, pd.NA, pd.NA],
            "SDQ_REASON": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "SDQ1"],
        }
    )

    fake_dfs = {"Episodes": eps, "OC2": oc2, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {
        "OC2": [
            1,
        ]
    }
