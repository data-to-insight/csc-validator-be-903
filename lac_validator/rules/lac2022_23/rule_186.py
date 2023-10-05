import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,  # Check 'Episodes' present before use!
)


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

    collection_start_str = dfs["metadata"]["collection_start"]
    collection_end_str = dfs["metadata"]["collection_end"]

    collection_start = pd.to_datetime(
        collection_start_str, format="%d/%m/%Y", errors="coerce"
    )
    collection_end = pd.to_datetime(
        collection_end_str, format="%d/%m/%Y", errors="coerce"
    )
    oc2["DOB_dt"] = pd.to_datetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")

    oc2 = add_CLA_column(dfs, "OC2")

    oc2["4th_bday"] = oc2["DOB_dt"] + pd.DateOffset(years=4)
    oc2["17th_bday"] = oc2["DOB_dt"] + pd.DateOffset(years=17)
    error_mask = (
        (oc2["4th_bday"] <= collection_start)
        & (oc2["17th_bday"] > collection_end)
        & oc2["CONTINUOUSLY_LOOKED_AFTER"]
        & oc2[["SDQ_SCORE", "SDQ_REASON"]].isna().all(axis=1)
    )

    oc2_errors = oc2.loc[error_mask].index.to_list()

    return {"OC2": oc2_errors}


def test_validate():
    import pandas as pd

    metadata = {"collection_start": "01/04/1980", "collection_end": "31/03/1981"}

    eps = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "DECOM": "31/03/1980",
                "DEC": "31/12/1980",
                "LS": "C2",
                "REC": "X1",
                "RNE": "o",
            },  # Pass
            {
                "CHILD": "1",
                "DECOM": "31/12/1980",
                "DEC": pd.NA,
                "LS": "C2",
                "REC": pd.NA,
                "RNE": "o",
            },  #Pass
            {
                "CHILD": "2",
                "DECOM": "31/03/1980",
                "DEC": pd.NA,
                "LS": "C2",
                "REC": pd.NA,
                "RNE": "o",
            },  #Pass
            {
                "CHILD": "3",
                "DECOM": "31/03/1980",
                "DEC": pd.NA,
                "LS": "C2",
                "REC": pd.NA,
                "RNE": "o",
            },  #Pass
            {
                "CHILD": "4",
                "DECOM": "31/03/1980",
                "DEC": pd.NA,
                "LS": "C2",
                "REC": pd.NA,
                "RNE": "o",
            },  #Fail
            {
                "CHILD": "5",
                "DECOM": "31/03/1980",
                "DEC": pd.NA,
                "LS": "C2",
                "REC": pd.NA,
                "RNE": "o",
            },  #Ignore
            {
                "CHILD": "6",
                "DECOM": "31/03/1980",
                "DEC": pd.NA,
                "LS": "C2",
                "REC": pd.NA,
                "RNE": "o",
            },  #Ignore
            {
                "CHILD": "7",
                "DECOM": "31/05/1980",
                "DEC": pd.NA,
                "LS": "C2",
                "REC": pd.NA,
                "RNE": "S",
            },  #Ignore
            {
                "CHILD": "8",
                "DECOM": "31/03/1980",
                "DEC": "30/03/1981",
                "LS": "C2",
                "REC": "E4a",
                "RNE": "o",
            },  #Ignore
            {
                "CHILD": "9",
                "DECOM": "31/03/1980",
                "DEC": pd.NA,
                "LS": "V4",
                "REC": pd.NA,
                "RNE": "o",
            },  #Ignore
        ]
    )

    oc2 = pd.DataFrame(
        {   # 0 Pass, 1 Pass, 2 Pass, 3 Fail (no value), 4 Ignore (age), 5 Ignore (age), 
            # 6 Ignore (duration), 7 Ignore (duration), 8 Ignore (LS), 9 Ignore (unmatched)
            "CHILD": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "DOB": [
                "01/04/1970",
                "01/04/1970",
                "01/04/1970",
                "01/04/1970",
                "01/04/1960", #20yrs
                "01/04/1978", #2yrs
                "01/04/1970",
                "01/04/1970",
                "01/04/1970",
                "01/04/1970",
            ],
            "SDQ_SCORE": ["10", "1O", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
            "SDQ_REASON": ["SDQ1", pd.NA, "SDQ2", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
        }
    )

    fake_dfs = {"Episodes": eps, "OC2": oc2, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {
        "OC2": [
            3,
        ]
    }
