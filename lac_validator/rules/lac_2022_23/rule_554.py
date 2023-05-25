import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="554",
    message="Date of decision that the child should be placed for adoption should be on or prior to the date that the placement order was granted. [NOTE: This rule may result in false positives or false negatives if relevant episodes are in previous years; please check carefully!]",
    affected_fields=["DATE_PLACED", "DECOM", "LS"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placed_adoption = dfs["PlacedAdoption"]

        # convert dates from string format to datetime format.
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        placed_adoption["DATE_PLACED"] = pd.to_datetime(
            placed_adoption["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
        )

        # Keep original index values as a column
        episodes["eps_index"] = episodes.index
        placed_adoption["pa_index"] = placed_adoption.index

        # select the first episodes with LS==E1
        e1_episodes = episodes.loc[episodes["LS"] == "E1"]
        first_e1_eps = e1_episodes.loc[e1_episodes.groupby("CHILD")["DECOM"].idxmin()]

        # merge
        merged = first_e1_eps.merge(placed_adoption, on="CHILD", how="left")

        # Where <LS> = 'E1' <DATE_PLACED> should be <= <DECOM> of first episode in <PERIOD_OF_CARE> with <LS> = 'E1'
        mask = merged["DATE_PLACED"] > merged["DECOM"]

        # error locations
        eps_error_locs = merged.loc[mask, "eps_index"]
        pa_error_locs = merged.loc[mask, "pa_index"]

        return {
            "Episodes": eps_error_locs.tolist(),
            "PlacedAdoption": pa_error_locs.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_placed_adoption = pd.DataFrame(
        [
            {"CHILD": 101, "DATE_PLACED": "26/05/2022"},
            # 0
            {"CHILD": 102, "DATE_PLACED": pd.NA},
            # 1
            {
                "CHILD": 103,
                "DATE_PLACED": "26/05/2020",
            },  # 2
            {"CHILD": 104, "DATE_PLACED": "22/01/2020"},
            # 3
            {
                "CHILD": 105,
                "DATE_PLACED": "11/01/2020",
            },  # 4
        ]
    )
    fake_data_episodes = pd.DataFrame(
        [
            # first E1 episode is first episode
            {
                "CHILD": 101,
                "DECOM": "01/01/2020",
                "LS": "E1",
            },  # 0 fail DATE_PLACED>DECOM
            {
                "CHILD": 101,
                "DECOM": "11/01/2020",
                "LS": "T1",
            },  # 1
            {
                "CHILD": 101,
                "DECOM": "22/01/2020",
                "LS": "A3",
            },  # 2
            # no E1 episode
            {
                "CHILD": 102,
                "DECOM": "11/01/2020",
                "LS": "A4",
            },  # 4
            {
                "CHILD": 102,
                "DECOM": "01/01/2020",
                "LS": "U1",
            },  # 3
            # first E1 episode is not first episode
            {
                "CHILD": 103,
                "DECOM": "01/01/2020",
                "LS": "U1",
            },  # 5
            {
                "CHILD": 103,
                "DECOM": "22/07/2020",
                "LS": "E1",
            },  # 6 pass
            {
                "CHILD": 103,
                "DECOM": "11/01/2020",
                "LS": "T2",
            },  # 7
            {
                "CHILD": 104,
                "DECOM": "01/02/2016",
                "LS": "E1",
            },  # 8 fail DATE_PLACED>DECOM
            {
                "CHILD": 104,
                "DECOM": "11/01/2020",
                "LS": "X1",
            },  # 9
            {
                "CHILD": 104,
                "DECOM": "01/01/2020",
                "LS": "A3",
            },  # 10
            {
                "CHILD": 105,
                "DECOM": "11/01/2020",
                "LS": "E1",
            },  # 11 pass DATE_PLACED equals DECOM
            {
                "CHILD": 105,
                "DECOM": "01/01/2020",
                "LS": pd.NA,
            },  # 12
        ]
    )
    fake_dfs = {"Episodes": fake_data_episodes, "PlacedAdoption": fake_placed_adoption}
    
    result = validate(fake_dfs)
    assert result == {"Episodes": [0, 8], "PlacedAdoption": [0, 3]}
