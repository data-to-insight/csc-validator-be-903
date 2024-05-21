import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="1010",
    message="This child has no episodes loaded for current year even though there was an open episode of "
    + "care at the end of the previous year, and care leaver data has been entered.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
    tables=["Episodes", "Episodes_last", "OC3"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Episodes_last" not in dfs or "OC3" not in dfs:
        return {}

    else:
        episodes = dfs["Episodes"]
        episodes_last = dfs["Episodes_last"]
        oc3 = dfs["OC3"]

        # convert DECOM to datetime, drop missing/invalid sort by CHILD then DECOM,
        episodes_last["DECOM"] = pd.to_datetime(
            episodes_last["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes_last = episodes_last.dropna(subset=["DECOM"]).sort_values(
            ["CHILD", "DECOM"], ascending=True
        )

        # Keep only the final episode for each child (ie where the following row has a different CHILD value)
        episodes_last = episodes_last[
            episodes_last["CHILD"].shift(-1) != episodes_last["CHILD"]
        ]
        # Keep only the final episodes that were still open
        episodes_last = episodes_last[episodes_last["DEC"].isna()]

        # The remaining children ought to have episode data in the current year if they are in OC3
        has_current_episodes = oc3["CHILD"].isin(episodes["CHILD"])
        has_open_episode_last = oc3["CHILD"].isin(episodes_last["CHILD"])

        error_mask = ~has_current_episodes & has_open_episode_last

        validation_error_locations = oc3.index[error_mask]

        return {"OC3": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_episodes_prev = pd.DataFrame(
        {
            "CHILD": ["101", "101", "102", "102", "103", "103", "103"],
            "DEC": [
                "20/06/2020",
                pd.NA,  # ok - has current episodes
                pd.NA,
                "14/03/2021",  # ok - 'open' episode not latest by DECOM
                "01/01/2020",
                pd.NA,
                "01/05/2020",
            ],  # Fail!
            "DECOM": [
                "01/01/2020",
                "11/11/2020",
                "03/10/2020",
                "11/11/2020",
                "01/01/2020",
                "11/11/2020",
                "01/02/2020",
            ],
        }
    )

    fake_episodes = pd.DataFrame({"CHILD": ["101"], "DEC": ["20/05/2021"]})

    fake_oc3 = pd.DataFrame({"CHILD": ["101", "102", "103"]})

    fake_dfs = {
        "Episodes": fake_episodes,
        "Episodes_last": fake_episodes_prev,
        "OC3": fake_oc3,
    }

    result = validate(fake_dfs)

    assert result == {"OC3": [2]}
