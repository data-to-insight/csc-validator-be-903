import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="1010",
    message="This child has no episodes loaded for current year even though there was an open episode of "
    + "care at the end of the previous year, and care leaver data has been entered.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Episodeslast" not in dfs or "OC3" not in dfs:
        return {}

    else:
        episodes = dfs["Episodes"]
        episodeslast = dfs["Episodeslast"]
        oc3 = dfs["OC3"]

        # convert DECOM to datetime, drop missing/invalid sort by CHILD then DECOM,
        episodeslast["DECOM"] = pd.todatetime(
            episodeslast["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodeslast = episodeslast.dropna(subset=["DECOM"]).sortvalues(
            ["CHILD", "DECOM"], ascending=True
        )

        # Keep only the final episode for each child (ie where the following row has a different CHILD value)
        episodeslast = episodeslast[
            episodeslast["CHILD"].shift(-1) != episodeslast["CHILD"]
        ]
        # Keep only the final episodes that were still open
        episodeslast = episodeslast[episodeslast["DEC"].isna()]

        # The remaining children ought to have episode data in the current year if they are in OC3
        hascurrentepisodes = oc3["CHILD"].isin(episodes["CHILD"])
        hasopenepisodelast = oc3["CHILD"].isin(episodeslast["CHILD"])

        errormask = ~hascurrentepisodes & hasopenepisodelast

        validationerrorlocations = oc3.index[errormask]

        return {"OC3": validationerrorlocations.tolist()}


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

    erro_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [2]}
