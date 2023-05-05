import pandas as pd

from validator903.types import ErrorDefinition


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
        ad1["DATEINT"] = pd.todatetime(
            ad1["DATEINT"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # select the earliest episodes with RNE =  S
        epsrne = episodes[episodes["RNE"] == "S"]
        lastepsidxs = epsrne.groupby("CHILD")["DECOM"].idxmax()
        lasteps = epsrne.loc[lastepsidxs]

        # prepare to merge
        ad1.resetindex(inplace=True)
        lasteps.resetindex(inplace=True)
        merged = lasteps.merge(ad1, how="left", on="CHILD", suffixes=["eps", "ad1"])

        # <DATEPLACED> cannot be prior to <DECOM> of the first episode with <RNE> = 'S'
        mask = merged["DATEINT"] < merged["DECOM"]

        epserrorlocs = merged.loc[mask, "indexeps"]
        ad1errorlocs = merged.loc[mask, "indexad1"]

        return {"Episodes": epserrorlocs.tolist(), "AD1": ad1errorlocs.tolist()}


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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 9], "AD1": [0, 4]}
