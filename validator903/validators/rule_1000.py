from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="1000",
        description="This child is recorded as having died in care and therefore should not have the care leaver information completed. [NOTE: This only tests the current and previous year data loaded into the tool]",
        affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "OC3" not in dfs:
            return {}

        else:
            episodes = dfs["Episodes"]
            oc3 = dfs["OC3"]

            episodes_ended_e2 = episodes["REC"].str.upper().astype(str).isin(["E2"])
            episodes = episodes.loc[episodes_ended_e2]

            if "Episodes_last" in dfs:
                episodes_last = dfs["Episodes_last"]
                episodes_last_ended_e2 = (
                    episodes_last["REC"].str.upper().astype(str).isin(["E2"])
                )
                episodes_last = episodes_last.loc[episodes_last_ended_e2]
                has_previous_e2 = oc3["CHILD"].isin(episodes_last["CHILD"])
                has_current_e2 = oc3["CHILD"].isin(episodes["CHILD"])
                error_mask = has_current_e2 | has_previous_e2
            else:
                has_current_e2 = oc3["CHILD"].isin(episodes["CHILD"])
                error_mask = has_current_e2

            validation_error_locations = oc3.index[error_mask]

            return {"OC3": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_episodes_prev = pd.DataFrame(
        {
            "CHILD": ["101", "101", "102", "102", "103"],
            "REC": ["X1", pd.NA, pd.NA, "E2", "E4a"],
        }
    )

    fake_episodes = pd.DataFrame({"CHILD": ["104", "105"], "REC": ["X1", "E2"]})

    fake_oc3 = pd.DataFrame({"CHILD": ["101", "102", "103", "104", "105"]})

    erro_defn, error_func = validate()

    fake_dfs = {
        "Episodes": fake_episodes,
        "Episodes_last": fake_episodes_prev,
        "OC3": fake_oc3,
    }
    result = error_func(fake_dfs)
    assert result == {"OC3": [1, 4]}

    fake_dfs = {"Episodes": fake_episodes, "OC3": fake_oc3}
    result = error_func(fake_dfs)
    assert result == {"OC3": [4]}
