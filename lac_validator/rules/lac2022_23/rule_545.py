import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,  # Check 'Episodes' present before use!
)


@rule_definition(
    code="545",
    message="Child is aged under 5 at 31 March and has been looked after continuously for 12 months yet health promotion information has not been completed.",
    affected_fields=["DOB", "HEALTH_CHECK"],
    tables=["OC2"],
)
def validate(dfs):
    if "OC2" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]
        collection_end = dfs["metadata"]["collection_end"]
        # add CLA column
        oc2 = add_CLA_column(dfs, "OC2")

        # to datetime
        oc2["DOB"] = pd.to_datetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )

        # If <DOB> < 5 years prior to <COLLECTION_END_DATE>and<CONTINUOUSLY_LOOKED_AFTER>= 'Y' then<HEALTH_CHECK>` should be provided.
        mask = (
            (collection_end < (oc2["DOB"] + pd.offsets.DateOffset(years=5)))
            & oc2["CONTINUOUSLY_LOOKED_AFTER"]
            & oc2["HEALTH_CHECK"].isna()
        )
        error_locations = oc2.index[mask]
        return {"OC2": error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DECOM": "01/03/1980",
                "DEC": "31/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # CLA
            {
                "CHILD": 102,
                "DECOM": "01/03/1980",
                "DEC": "30/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # CLA
            {
                "CHILD": 103,
                "DECOM": "01/03/1980",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # CLA
            {
                "CHILD": 104,
                "DECOM": "01/02/1970",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },  # CLA
            {
                "CHILD": 105,
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },  # CLA
            {
                "CHILD": 105,
                "DECOM": "01/01/1981",
                "DEC": "01/01/1983",
                "LS": "o",
                "REC": "oo",
                "RNE": "o",
            },  # CLA
            {
                "CHILD": 106,
                "DECOM": "01/03/1980",
                "DEC": "01/01/1982",
                "LS": "V3",
                "REC": "X1",
                "RNE": "o",
            },  # not CLA: V3
            {
                "CHILD": 107,
                "DECOM": "01/03/1980",
                "DEC": "01/01/1982",
                "LS": "V3",
                "REC": "!!",
                "RNE": "o",
            },  # not CLA: REC
        ]
    )
    fake_data = pd.DataFrame(
        {
            "CHILD": [101, 102, 103, 104, 105, 106, 107, 333],
            "DOB": [
                "08/03/1973",
                "22/06/1977",
                pd.NA,
                "13/10/2000",
                "10/01/1978",
                "01/01/1978",
                "01/01/1978",
                "01/01/1978",
            ],
            "HEALTH_CHECK": [pd.NA, pd.NA, pd.NA, 1, pd.NA, pd.NA, pd.NA, pd.NA],
            # 0 pass: over 5
            # 1 fail : CLA is true, under 5, and HEALTH_CHECK is not provided
            # 2 pass: DOB is nan
            # 3 pass: under 5 (born in future), but HEALTH_CHECK provided
            # 4 fail: CLA is true, under 5, and HEALTH_CHECK is not provided
            # 5 pass: not CLA
            # 6 pass: not CLA
            # 7 pass: not in episodes -> not CLA
        }
    )

    metadata = {"collection_start": "01/04/1980", "collection_end": "31/03/1981"}

    fake_dfs = {"OC2": fake_data, "metadata": metadata, "Episodes": fake_data_episodes}

    result = validate(fake_dfs)

    assert result == {"OC2": [1, 4]}
