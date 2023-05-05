import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="452",
    message="Contradiction between local authority of placement code in the last episode of the previous year and in the first episode of the current year.",
    affected_fields=["PL_LA"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    if "Episodeslast" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodeslast = dfs["Episodeslast"]

        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodeslast["DECOM"] = pd.todatetime(
            episodeslast["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        episodesmin = episodes.groupby("CHILD")["DECOM"].idxmin()
        episodeslastmax = episodeslast.groupby("CHILD")["DECOM"].idxmax()

        episodes = episodes[episodes.index.isin(episodesmin)]
        episodeslast = episodeslast[episodeslast.index.isin(episodeslastmax)]

        episodesmerged = (
            episodes.resetindex()
            .merge(
                episodeslast,
                how="left",
                on=["CHILD"],
                suffixes=("", "last"),
                indicator=True,
            )
            .setindex("index")
        )

        inbothyears = episodesmerged["merge"] == "both"
        samerne = episodesmerged["RNE"] == episodesmerged["RNElast"]
        lastyearopen = episodesmerged["DEClast"].isna()
        differentplla = episodesmerged["PLLA"].astype(str) != episodesmerged[
            "PLLAlast"
        ].astype(str)

        errormask = inbothyears & samerne & lastyearopen & differentplla

        validationerrorlocations = episodes.index[errormask]

        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    error_defn, error_func = validate()
    result = error_func(fake_dfs__452_453_503G_503H)
    assert result == {"Episodes": [4, 6]}
