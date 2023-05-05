import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="NoE",
    message="This child has no episodes loaded for previous year even though child started to be looked after before this current year.",
    affected_fields=["DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Episodeslast" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodeslast = dfs["Episodeslast"]
        episodeslast["DECOM"] = pd.todatetime(
            episodeslast["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        collectionstart = pd.todatetime(
            dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
        )

        episodesbeforeyear = episodes[episodes["DECOM"] < collectionstart]

        episodesmerged = (
            episodesbeforeyear.resetindex()
            .merge(episodeslast, how="left", on=["CHILD"], indicator=True)
            .setindex("index")
        )

        episodesnotmatched = episodesmerged[episodesmerged["merge"] == "leftonly"]

        errormask = episodes.index.isin(episodesnotmatched.index)

        errorlocations = episodes.index[errormask]

        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103"],
            "DECOM": ["14/03/2021", "08/09/2021", "03/10/2020"],
        }
    )

    fake_data_prev = pd.DataFrame(
        {"CHILD": ["101", "102"], "DECOM": ["14/03/2021", "16/06/2019"]}
    )

    metadata = {"collection_start": "01/04/2021"}

    fake_dfs = {
        "Episodes": fake_data,
        "Episodes_last": fake_data_prev,
        "metadata": metadata,
    }

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2]}
