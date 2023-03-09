import pandas as pd

from validator903.types import ErrorDefinition
from validator903.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,
)  # Check 'Episodes' present before use!


def validate():
    error = ErrorDefinition(
        code="186",
        description="Children aged 4 or over at the start of the year and children aged under 17 at the "
        + "end of the year and who have been looked after for at least 12 months continuously "
        + "should have a Strengths and Difficulties (SDQ) score completed.",
        affected_fields=["SDQ_SCORE"],
    )

    def _validate(dfs):
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
            & oc2[["SDQ_SCORE", "SDQ_REASON"]].isna().any(axis=1)
        )

        oc2_errors = oc2.loc[error_mask].index.to_list()

        return {"OC2": oc2_errors}

    return error, _validate


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
