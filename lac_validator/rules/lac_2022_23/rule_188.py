import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="188",
    message="Child is aged under 4 years at the end of the year, "
    "but a Strengths and Difficulties (SDQ) score or a reason "
    "for no SDQ score has been completed. ",
    affected_fields=["SDQ_SCORE", "SDQ_REASON"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}

    oc2 = dfs["OC2"]

    collectionendstr = dfs["metadata"]["collectionend"]

    collectionend = pd.todatetime(collectionendstr, format="%d/%m/%Y", errors="coerce")
    oc2["DOBdt"] = pd.todatetime(oc2["DOB"], format="%d/%m/%Y", errors="coerce")

    oc2["4thbday"] = oc2["DOBdt"] + pd.DateOffset(years=4)
    errormask = (oc2["4thbday"] > collectionend) & oc2[
        ["SDQSCORE", "SDQREASON"]
    ].notna().any(axis=1)

    oc2errors = oc2.loc[errormask].index.tolist()

    return {"OC2": oc2errors}


def test_validate():
    import pandas as pd

    metadata = {"collection_end": "31/03/1981"}

    oc2 = pd.DataFrame(
        {
            "CHILD": ["0", "1", "2", "3", "4"],
            "DOB": [
                "01/01/1970",
                "01/01/1980",
                "01/01/1970",
                "31/03/1977",
                "01/04/1977",
            ],
            "SDQ_SCORE": ["OK", "!!!", pd.NA, "OK", "!!!"],
        }
    )

    oc2["SDQ_REASON"] = pd.NA

    fake_dfs = {"OC2": oc2, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [1, 4]}
