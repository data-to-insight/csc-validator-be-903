from validator903.types import ErrorDefinition


@rule_definition(
    code="197a",
    message="Reason for no Strengths and Difficulties (SDQ) score is not required if Strengths and Difficulties Questionnaire score is filled in.",
    affected_fields=["SDQ_SCORE", "SDQ_REASON"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]

        sdqfilledin = oc2["SDQSCORE"].notna()
        reasonfilledin = oc2["SDQREASON"].notna()

        errormask = sdqfilledin & reasonfilledin
        validationerrorlocations = oc2.index[errormask]

        return {"OC2": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SDQ_SCORE": [0, pd.NA, 10, "1", pd.NA],
            "SDQ_REASON": ["XXX", pd.NA, pd.NA, "XXX", "XXX"],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [0, 3]}
