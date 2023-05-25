import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="189",
    message="Child is aged 17 years or over at the beginning of the year, but an Strengths and Difficulties "
    + "(SDQ) score or a reason for no Strengths and Difficulties (SDQ) score has been completed.",
    affected_fields=["DOB", "SDQ_SCORE", "SDQ_REASON"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]
        collection_start = dfs["metadata"]["collection_start"]

        # datetime format allows appropriate comparison between dates
        oc2["DOB"] = pd.to_datetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")
        collection_start = pd.to_datetime(
            collection_start, format="%d/%m/%Y", errors="coerce"
        )

        # If <DOB> >17 years prior to <COLLECTION_START_DATE> then <SDQ_SCORE> and <SDQ_REASON> should not be provided
        mask = ((oc2["DOB"] + pd.offsets.DateOffset(years=17)) <= collection_start) & (
            oc2["SDQ_REASON"].notna() | oc2["SDQ_SCORE"].notna()
        )
        # That is, raise error if collection_start > DOB + 17years
        oc_error_locs = oc2.index[mask]
        return {"OC2": oc_error_locs.tolist()}


def test_validate():
    import pandas as pd

    metadata = {"collection_start": "01/04/1980"}

    oc2 = pd.DataFrame(
        {
            "CHILD": ["0", "1", "2", "3"],
            "DOB": ["01/04/1963", "02/04/1963", "01/01/1970", "31/03/1960"],
            "SDQ_SCORE": ["!!!", "OK", pd.NA, pd.NA],
            "SDQ_REASON": [pd.NA, pd.NA, pd.NA, pd.NA],
        }
    )

    fake_dfs = {"OC2": oc2, "metadata": metadata}

    

    result = validate(fake_dfs)

    assert result == {
        "OC2": [
            0,
        ]
    }
