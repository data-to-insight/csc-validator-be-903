import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


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
        placed_adoption = dfs["PlacedAdoption"]

        # to datetime
        placed_adoption["DATE_PLACED"] = pd.to_datetime(
            placed_adoption["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # select the earliest episodes with RNE =  S
        eps_rne = episodes[episodes["RNE"] == "S"]
        first_eps_idxs = eps_rne.groupby("CHILD")["DECOM"].idxmin()
        first_eps = eps_rne.loc[first_eps_idxs]
        # prepare to merge
        placed_adoption.reset_index(inplace=True)
        first_eps.reset_index(inplace=True)
        merged = first_eps.merge(
            placed_adoption, how="left", on="CHILD", suffixes=["_eps", "_pa"]
        )

        # <DATE_PLACED> cannot be prior to <DECOM> of the first episode with <RNE> = 'S'
        mask = merged["DATE_PLACED"] < merged["DECOM"]
        eps_error_locs = merged.loc[mask, "index_eps"]
        pa_error_locs = merged.loc[mask, "index_pa"]
        return {
            "Episodes": eps_error_locs.tolist(),
            "PlacedAdoption": pa_error_locs.tolist(),
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
