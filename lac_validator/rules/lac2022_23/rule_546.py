import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.utils import (
    add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column,  # Check 'Episodes' present before use!
)


@rule_definition(
    code="546",
    message="Children aged 5 or over at 31 March should not have health promotion information completed.",
    affected_fields=["DOB", "HEALTH_CHECK"],
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

        # If <DOB> >= 5 years prior to<COLLECTION_END_DATE>and<CONTINUOUSLY_LOOKED_AFTER>= 'Y' then<HEALTH_CHECK>` should not be provided
        mask = (
            (collection_end >= (oc2["DOB"] + pd.offsets.DateOffset(years=5)))
            & oc2["CONTINUOUSLY_LOOKED_AFTER"]
            & oc2["HEALTH_CHECK"].notna()
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
            },
            {
                "CHILD": 102,
                "DECOM": "01/03/1980",
                "DEC": "30/03/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
            {
                "CHILD": 103,
                "DECOM": "01/03/1980",
                "DEC": "01/01/1981",
                "LS": "V3",
                "REC": "X1",
                "RNE": "o",
            },  # False
            {
                "CHILD": 104,
                "DECOM": "01/02/1970",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "!!",
                "RNE": "o",
            },
            {
                "CHILD": 105,
                "DECOM": "01/03/1979",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
                "RNE": "o",
            },
        ]
    )
    fake_data = pd.DataFrame(
        {
            "CHILD": [101, 102, 103, 104, 105],
            "DOB": ["08/03/1963", "22/06/1957", pd.NA, "13/10/2000", "10/01/1948"],
            "HEALTH_CHECK": [1, 1, pd.NA, 1, pd.NA],
            # 0 fail because conditions are met but HEALTH_CHECK is provided
            # 1 fail because conditions are met but HEALTH_CHECK is provided
            # 2 ignore: DOB is nan
            # 3 ignore: CLA is false
            # 4 pass
        }
    )

    metadata = {"collection_start": "01/04/1980", "collection_end": "31/03/1981"}

    fake_dfs = {"OC2": fake_data, "metadata": metadata, "Episodes": fake_data_episodes}

    result = validate(fake_dfs)

    assert result == {"OC2": [0, 1]}
