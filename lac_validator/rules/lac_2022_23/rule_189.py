import pandas as pd

from validator903.types import ErrorDefinition


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
        collectionstart = dfs["metadata"]["collectionstart"]

        # datetime format allows appropriate comparison between dates
        oc2["DOB"] = pd.todatetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")
        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )

        # If <DOB> >17 years prior to <COLLECTIONSTARTDATE> then <SDQSCORE> and <SDQREASON> should not be provided
        mask = ((oc2["DOB"] + pd.offsets.DateOffset(years=17)) <= collectionstart) & (
            oc2["SDQREASON"].notna() | oc2["SDQSCORE"].notna()
        )
        # That is, raise error if collectionstart > DOB + 17years
        ocerrorlocs = oc2.index[mask]
        return {"OC2": ocerrorlocs.tolist()}


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

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {
        "OC2": [
            0,
        ]
    }
