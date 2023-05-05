import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="1003",
    message="Date of LA's decision that a child should be placed for adoption is before the child started to be looked after.",
    affected_fields=["DATE_PLACED", "DECOM", "RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placedadoption = dfs["PlacedAdoption"]

        # to datetime
        placedadoption["DATEPLACED"] = pd.todatetime(
            placedadoption["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # select the earliest episodes with RNE =  S
        epsrne = episodes[episodes["RNE"] == "S"]
        firstepsidxs = epsrne.groupby("CHILD")["DECOM"].idxmin()
        firsteps = epsrne.loc[firstepsidxs]
        # prepare to merge
        placedadoption.resetindex(inplace=True)
        firsteps.resetindex(inplace=True)
        merged = firsteps.merge(
            placedadoption, how="left", on="CHILD", suffixes=["eps", "pa"]
        )

        # <DATEPLACED> cannot be prior to <DECOM> of the first episode with <RNE> = 'S'
        mask = merged["DATEPLACED"] < merged["DECOM"]
        epserrorlocs = merged.loc[mask, "indexeps"]
        paerrorlocs = merged.loc[mask, "indexpa"]
        return {
            "Episodes": epserrorlocs.tolist(),
            "PlacedAdoption": paerrorlocs.tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        [
            {"CHILD": 101, "DECOM": "01/03/1980", "RNE": "S"},  # 0 fail
            {"CHILD": 102, "DECOM": "01/03/1980", "RNE": "o"},
            {
                "CHILD": 102,
                "DECOM": "01/03/1980",
                "RNE": "S",
            },  # 2 ignore DATE_PLACED is nan
            {"CHILD": 103, "DECOM": "01/02/1970", "RNE": "o"},
            {"CHILD": 103, "DECOM": "01/03/1979", "RNE": "S"},  # 4 fail
            {"CHILD": 103, "DECOM": "01/01/1981", "RNE": "S"},
            {"CHILD": 104, "DECOM": "01/03/1979", "RNE": "o"},  # ignore no RNE is S
            {"CHILD": 104, "DECOM": "01/01/1981", "RNE": "o"},
            {"CHILD": 105, "DECOM": "01/03/1979", "RNE": "o"},
            {"CHILD": 105, "DECOM": "01/01/1981", "RNE": "o"},
            {"CHILD": 105, "DECOM": "01/01/1981", "RNE": "S"},  # 10 pass
        ]
    )
    fake_placed_adoption = pd.DataFrame(
        [
            {"CHILD": 101, "DATE_PLACED": "26/05/1978"},  # 0 fail
            {"CHILD": 102, "DATE_PLACED": pd.NA},  # 1
            {"CHILD": 103, "DATE_PLACED": "26/05/1970"},  # 2 fail
            {"CHILD": 104, "DATE_PLACED": "01/02/1960"},  # 3
            {"CHILD": 105, "DATE_PLACED": "26/05/2019"},  # 4
        ]
    )
    fake_dfs = {"Episodes": fake_data_episodes, "PlacedAdoption": fake_placed_adoption}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 4], "PlacedAdoption": [0, 2]}
