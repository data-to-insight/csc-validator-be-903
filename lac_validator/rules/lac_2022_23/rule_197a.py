from lac_validator.rule_engine import rule_definition


import pandas as pd


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

        sdq_filled_in = oc2["SDQ_SCORE"].notna()
        reason_filled_in = oc2["SDQ_REASON"].notna()

        error_mask = sdq_filled_in & reason_filled_in
        validation_error_locations = oc2.index[error_mask]

        return {"OC2": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SDQ_SCORE": [0, pd.NA, 10, "1", pd.NA],
            "SDQ_REASON": ["XXX", pd.NA, pd.NA, "XXX", "XXX"],
        }
    )

    fake_dfs = {"OC2": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"OC2": [0, 3]}
