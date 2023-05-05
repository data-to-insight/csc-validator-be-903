from validator903.types import ErrorDefinition


@rule_definition(
    code="1000",
    message="This child is recorded as having died in care and therefore should not have the care leaver information completed. [NOTE: This only tests the current and previous year data loaded into the tool]",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "OC3" not in dfs:
        return {}

    else:
        episodes = dfs["Episodes"]
        oc3 = dfs["OC3"]

        episodesendede2 = episodes["REC"].str.upper().astype(str).isin(["E2"])
        episodes = episodes.loc[episodesendede2]

        if "Episodeslast" in dfs:
            episodeslast = dfs["Episodeslast"]
            episodeslastendede2 = (
                episodeslast["REC"].str.upper().astype(str).isin(["E2"])
            )
            episodeslast = episodeslast.loc[episodeslastendede2]
            haspreviouse2 = oc3["CHILD"].isin(episodeslast["CHILD"])
            hascurrente2 = oc3["CHILD"].isin(episodes["CHILD"])
            errormask = hascurrente2 | haspreviouse2
        else:
            hascurrente2 = oc3["CHILD"].isin(episodes["CHILD"])
            errormask = hascurrente2

        validationerrorlocations = oc3.index[errormask]

        return {"OC3": validationerrorlocations.tolist()}


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
