from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="1002",
    message="This child has no previous episodes of care, therefore should not have care leaver information recorded. "
    "[NOTE: This tool can only test the current and previous year data loaded into the tool - this "
    "check may generate false positives if a child had episodes prior to last year's collection.]",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
    tables=["Episodes", "OC3", "Episodes_last"],
)
def validate(dfs):
    if "Episodes" not in dfs or "OC3" not in dfs or "Episodes_last" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        oc3 = dfs["OC3"]

        episodes_last = dfs["Episodes_last"]
        has_previous_episodes = oc3["CHILD"].isin(episodes_last["CHILD"])
        has_current_episodes = oc3["CHILD"].isin(episodes["CHILD"])
        error_mask = ~has_current_episodes & ~has_previous_episodes

        validation_error_locations = oc3.index[error_mask]

        return {"OC3": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_episodes_prev = pd.DataFrame(
        {
            "CHILD": ["101", "101", "102", "102", "103"],
            "DEC": ["20/06/2020", pd.NA, pd.NA, "14/03/2021", "06/08/2020"],
        }
    )

    fake_episodes = pd.DataFrame({"CHILD": ["101"], "DEC": ["20/05/2021"]})

    fake_oc3 = pd.DataFrame({"CHILD": ["101", "102", "103", "104"]})

    fake_dfs = {
        "Episodes": fake_episodes,
        "Episodes_last": fake_episodes_prev,
        "OC3": fake_oc3,
    }
    result = validate(fake_dfs)
    assert result == {"OC3": [3]}
