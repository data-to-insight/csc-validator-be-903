from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="197a",
        description="Reason for no Strengths and Difficulties (SDQ) score is not required if Strengths and Difficulties Questionnaire score is filled in.",
        affected_fields=["SDQ_SCORE", "SDQ_REASON"],
    )

    def _validate(dfs):
        if "OC2" not in dfs:
            return {}
        else:
            oc2 = dfs["OC2"]

            sdq_filled_in = oc2["SDQ_SCORE"].notna()
            reason_filled_in = oc2["SDQ_REASON"].notna()

            error_mask = sdq_filled_in & reason_filled_in
            validation_error_locations = oc2.index[error_mask]

            return {"OC2": validation_error_locations.tolist()}

    return error, _validate


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
