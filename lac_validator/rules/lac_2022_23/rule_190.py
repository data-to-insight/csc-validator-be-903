from lac_validator.rule_engine import rule_definition
from validator903.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,
)  # Check 'Episodes' present before use!


import pandas as pd


@rule_definition(
    code="190",
    message="Child has not been looked after continuously for at least 12 months at 31 March but one or more "
    "data items relating to children looked after for 12 months have been completed.",
    affected_fields=[
        "CONVICTED",
        "HEALTH_CHECK",
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ],  # AD1
)
def validate(dfs):
    if "OC2" not in dfs or "Episodes" not in dfs:
        return {}

    # add 'CONTINUOUSLY_LOOKED_AFTER' column
    oc2 = add_CLA_column(dfs, "OC2")

    should_be_blank = [
        "CONVICTED",
        "HEALTH_CHECK",
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ]

    mask = ~oc2["CONTINUOUSLY_LOOKED_AFTER"] & oc2[should_be_blank].notna().any(axis=1)
    error_locs = oc2[mask].index.to_list()

    return {"OC2": error_locs}


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
        ]
    )

    oc2 = pd.DataFrame(
        {
            "CHILD": ["9999999999", "1", "2", "3333", "99999999", "8888", "5"],
            "CONVICTED": ["!!!", "OK", pd.NA, pd.NA, pd.NA, "!!!", "OK"],
        }
    )
    other_oc2_cols = [
        "HEALTH_CHECK",
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ]
    oc2 = oc2.assign(**{col: pd.NA for col in other_oc2_cols})

    fake_dfs = {"Episodes": eps, "OC2": oc2, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [0, 5]}
