import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="180",
    message="Data entry for the strengths and difficulties questionnaire (SDQ) score is invalid.",
    affected_fields=["SDQ_SCORE"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]

        oc2["SDQSCOREnum"] = pd.tonumeric(oc2["SDQSCORE"], errors="coerce")

        errormask = oc2["SDQSCORE"].notna() & ~oc2["SDQSCOREnum"].isin(range(41))

        validationerrorlocations = oc2.index[errormask]

        return {"OC2": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SDQ_SCORE": ["10", 41, "58", 72, "0", 40, 39.5, 20.0, pd.NA, "XX"],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [1, 2, 3, 6, 9]}
