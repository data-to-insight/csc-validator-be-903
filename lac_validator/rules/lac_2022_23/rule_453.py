import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="453",
    message="Contradiction between placement distance in the last episode of the previous year and in the first episode of the current year.",
    affected_fields=["PL_DISTANCE"],
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
        episodes["PLDISTANCE"] = pd.tonumeric(episodes["PLDISTANCE"], errors="coerce")
        episodeslast["PLDISTANCE"] = pd.tonumeric(
            episodeslast["PLDISTANCE"], errors="coerce"
        )

        # drop rows with missing DECOM before finding idxmin/max, as invalid/missing values can lead to errors
        episodes = episodes.dropna(subset=["DECOM"])
        episodeslast = episodeslast.dropna(subset=["DECOM"])

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
        differentpldist = (
            abs(episodesmerged["PLDISTANCE"] - episodesmerged["PLDISTANCElast"]) >= 0.2
        )

        errormask = inbothyears & samerne & lastyearopen & differentpldist

        validationerrorlocations = episodes.index[errormask]

        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    error_defn, error_func = validate()

    result = error_func(fake_dfs__452_453_503G_503H)

    assert result == {"Episodes": [4]}
