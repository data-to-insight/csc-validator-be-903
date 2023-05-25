import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="334",
    message="Date child started to be looked after in latest period of care must be on or prior to the date should be placed for adoption. ",
    affected_fields=["DATE_INT", "DECOM", "RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "AD1" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        ad1 = dfs["AD1"]

        # to datetime
        ad1["DATE_INT"] = pd.to_datetime(
            ad1["DATE_INT"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # select the earliest episodes with RNE =  S
        eps_rne = episodes[episodes["RNE"] == "S"]
        last_eps_idxs = eps_rne.groupby("CHILD")["DECOM"].idxmax()
        last_eps = eps_rne.loc[last_eps_idxs]

        # prepare to merge
        ad1.reset_index(inplace=True)
        last_eps.reset_index(inplace=True)
        merged = last_eps.merge(ad1, how="left", on="CHILD", suffixes=["_eps", "_ad1"])

        # <DATE_PLACED> cannot be prior to <DECOM> of the first episode with <RNE> = 'S'
        mask = merged["DATE_INT"] < merged["DECOM"]

        eps_error_locs = merged.loc[mask, "index_eps"]
        ad1_error_locs = merged.loc[mask, "index_ad1"]

        return {"Episodes": eps_error_locs.tolist(), "AD1": ad1_error_locs.tolist()}


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
            {"CHILD": 103, "DECOM": "01/03/1979", "RNE": "S"},
            {"CHILD": 103, "DECOM": "01/01/1980", "RNE": "S"},  # 5 pass
            {"CHILD": 104, "DECOM": "01/03/1979", "RNE": "o"},  # ignore no RNE is S
            {"CHILD": 104, "DECOM": "01/01/1981", "RNE": "o"},
            {"CHILD": 105, "DECOM": "01/03/1979", "RNE": "o"},
            {"CHILD": 105, "DECOM": "01/01/2020", "RNE": "S"},  # 9 fail
            {"CHILD": 105, "DECOM": "26/05/2021", "RNE": "o"},
        ]
    )
    fake_placed_ad1 = pd.DataFrame(
        [
            {"CHILD": 101, "DATE_INT": "26/05/1978"},  # 0 fail
            {"CHILD": 102, "DATE_INT": pd.NA},  # 1
            {"CHILD": 103, "DATE_INT": "26/05/1981"},  # 2 pass
            {"CHILD": 104, "DATE_INT": "01/02/1960"},  # 3
            {"CHILD": 105, "DATE_INT": "26/05/2019"},  # 4 fail
        ]
    )
    fake_dfs = {"Episodes": fake_data_episodes, "AD1": fake_placed_ad1}
    
    result = validate(fake_dfs)
    assert result == {"Episodes": [0, 9], "AD1": [0, 4]}
