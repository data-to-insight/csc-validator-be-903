import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="196",
    message="Strengths and Difficulties (SDQ) reason is not a valid code.",
    affected_fields=["SDQ_REASON"],
    tables=["OC2"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}

    oc2 = dfs["OC2"]
    code_list = ["SDQ1", "SDQ2", "SDQ3", "SDQ4", "SDQ5"]

    mask = oc2["SDQ_REASON"].isin(code_list) | oc2["SDQ_REASON"].isna()

    validation_error_mask = ~mask
    validation_error_locations = oc2.index[validation_error_mask]

    return {"OC2": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SDQ_REASON": ["SDQ2", "sdq2", "", pd.NA],
        }
    )

    fake_dfs = {"OC2": fake_data}

    result = validate(fake_dfs)

    assert result == {"OC2": [1, 2]}
