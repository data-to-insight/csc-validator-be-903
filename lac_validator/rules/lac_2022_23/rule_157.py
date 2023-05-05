import pandas as pd

from validator903.types import ErrorDefinition
from validator903.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,
)  # Check 'Episodes' present before use!


@rule_definition(
    code="157",
    message="Child is aged 4 years or over at the beginning of the year or 16 years or under at the end of the "
    "year and Strengths and Difficulties Questionnaire (SDQ) 1 has been recorded as the reason for no "
    "Strengths and Difficulties Questionnaire (SDQ) score.",
    affected_fields=["SDQ_REASON", "DOB"],
)
def validate(dfs):
    if "OC2" not in dfs or "Episodes" not in dfs:
        return {}
    oc2 = addCLAcolumn(dfs, "OC2")

    start = pd.todatetime(
        dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
    )
    endo = pd.todatetime(
        dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
    )
    oc2["DOB"] = pd.todatetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")

    ERRRR = (
        oc2["CONTINUOUSLYLOOKEDAFTER"]
        & (oc2["DOB"] + pd.DateOffset(years=4) <= start)
        & (oc2["DOB"] + pd.DateOffset(years=16) >= endo)
        & oc2["SDQSCORE"].isna()
        & (oc2["SDQREASON"] == "SDQ1")
    )

    return {"OC2": oc2[ERRRR].index.tolist()}


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
                "CHILD": "3333",
                "DECOM": "01/03/1980",
                "DEC": "01/01/1981",
                "LS": "V3",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "4",
                "DECOM": "01/02/1970",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },
            {
                "CHILD": "5",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "5",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },
            {
                "CHILD": "6666",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },
            {
                "CHILD": "6666",
                "DECOM": "01/01/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": pd.NA,
                "RNE": "o",
            },
            {
                "CHILD": "7777",
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": "7777",
                "DECOM": "01/01/1981",
                "DEC": "01/07/1981",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },
            {
                "CHILD": "8888",
                "DECOM": "01/01/1981",
                "DEC": "31/03/1999",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },
        ]
    )

    oc2 = pd.DataFrame(
        {
            "CHILD": ["9999999999", "1", "2", "3333", "99999999", "8888", "5"],
            "SDQ_SCORE": ["OK", pd.NA, pd.NA, pd.NA, pd.NA, "OK", pd.NA],
            "SDQ_REASON": ["SDQ1", "SDQ1", "SDQ1", "OK", pd.NA, "OK", "OK!"],
            "DOB": [
                "01/04/1970",
                "31/03/1965",
                "01/04/1976",
                "01/04/1970",
                "01/04/1970",
                "01/04/1970",
                "01/07/1970",
            ],
        }
    )

    test_dfs = {"Episodes": eps, "OC2": oc2, "metadata": metadata}

    error_defn, error_func = validate()

    test_result = error_func(test_dfs)

    assert test_result == {"OC2": [1, 2]}
