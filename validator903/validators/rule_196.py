from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="196",
        description="Strengths and Difficulties (SDQ) reason is not a valid code.",
        affected_fields=["SDQ_REASON"],
    )

    def _validate(dfs):
        if "OC2" not in dfs:
            return {}

        oc2 = dfs["OC2"]
        code_list = ["SDQ1", "SDQ2", "SDQ3", "SDQ4", "SDQ5"]

        mask = oc2["SDQ_REASON"].isin(code_list) | oc2["SDQ_REASON"].isna()

        validation_error_mask = ~mask
        validation_error_locations = oc2.index[validation_error_mask]

        return {"OC2": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SDQ_REASON": ["SDQ2", "sdq2", "", pd.NA],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [1, 2]}
