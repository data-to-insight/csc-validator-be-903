from lac_validator.rule_engine import rule_definition
from validator903.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,
)  # Check 'Episodes' present before use!


import pandas as pd


@rule_definition(
    code="187",
    message="Child cannot be looked after continuously for 12 months at "
    + "31 March (OC2) and have any of adoption or care leavers returns completed.",
    affected_fields=[
        "DATE_INT",
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",  # OC3
        "IN_TOUCH",
        "ACTIV",
        "ACCOM",
    ],  # AD1
)
def validate(dfs):
    if "OC3" not in dfs or "AD1" not in dfs or "Episodes" not in dfs:
        return {}

    # add 'CONTINUOUSLY_LOOKED_AFTER' column
    ad1, oc3 = add_CLA_column(dfs, ["AD1", "OC3"])

    # OC3
    should_be_blank = ["IN_TOUCH", "ACTIV", "ACCOM"]
    oc3_mask = oc3["CONTINUOUSLY_LOOKED_AFTER"] & oc3[should_be_blank].notna().any(
        axis=1
    )
    oc3_error_locs = oc3[oc3_mask].index.to_list()

    # AD1
    should_be_blank = [
        "DATE_INT",
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ]
    ad1_mask = ad1["CONTINUOUSLY_LOOKED_AFTER"] & ad1[should_be_blank].notna().any(
        axis=1
    )
    ad1_error_locs = ad1[ad1_mask].index.to_list()

    return {"AD1": ad1_error_locs, "OC3": oc3_error_locs}


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
            },  # !! - False
            {
                "CHILD": "6666",
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
                "CHILD": "8888",
                "DECOM": "01/01/1981",
                "DEC": "31/03/1999",
                "LS": "o",
                "REC": "o",
                "RNE": "S",
            },  # False
            {
                "CHILD": "9",
                "DECOM": "05/04/1980",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "xx",
                "RNE": "S",
            },
            # nCLA True DECOM>col_start and RNE==S
            {
                "CHILD": "10",
                "DECOM": pd.NA,
                "DEC": "05/04/1980",
                "LS": "o",
                "REC": "xx",
                "RNE": "S",
            },
            # nCLA True DEC>col_start and REC!=X1
            {
                "CHILD": "11",
                "DECOM": pd.NA,
                "DEC": "05/04/1980",
                "LS": "V3",
                "REC": pd.NA,
                "RNE": "S",
            },
            # nCLA True DEC>col_start and LS in [V3, V4]
        ]
    )

    oc3 = pd.DataFrame(
        {
            "CHILD": [
                "9999999999",
                "1",
                "2",
                "3333",
                "99999999",
                "8888",
                "5",
                "9",
                "10",
                "11",
            ],
            "IN_TOUCH": [
                "OK",
                "!!!",
                pd.NA,
                "OK",
                pd.NA,
                pd.NA,
                pd.NA,
                "xx",
                "xx",
                "xx",
            ],
        }
    )
    other_oc3_cols = ["ACTIV", "ACCOM"]
    oc3 = oc3.assign(**{col: pd.NA for col in other_oc3_cols})

    ad1 = pd.DataFrame(
        {
            "CHILD": [
                "1",
                "2",
                "3333",
                "7777",
                "99999999",
                "8888",
                "5",
                "9",
                "10",
                "11",
            ],
            "DATE_INT": [
                pd.NA,
                pd.NA,
                "OK",
                "OK",
                pd.NA,
                pd.NA,
                "!!!",
                "xx",
                "xx",
                "xx",
            ],
        }
    )

    other_ad1_cols = [
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ]
    ad1 = ad1.assign(**{col: pd.NA for col in other_ad1_cols})

    fake_dfs = {"Episodes": eps, "OC3": oc3, "AD1": ad1, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {
        "OC3": [
            1,
        ],
        "AD1": [
            6,
        ],
    }
