import pandas as pd

from validator903.types import ErrorDefinition


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
        placedadoption = dfs["PlacedAdoption"]

        # convert dates from string format to datetime format.
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        placedadoption["DATEPLACED"] = pd.todatetime(
            placedadoption["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )

        # Keep original index values as a column
        episodes["epsindex"] = episodes.index
        placedadoption["paindex"] = placedadoption.index

        # select the first episodes with LS==E1
        e1episodes = episodes.loc[episodes["LS"] == "E1"]
        firste1eps = e1episodes.loc[e1episodes.groupby("CHILD")["DECOM"].idxmin()]

        # merge
        merged = firste1eps.merge(placedadoption, on="CHILD", how="left")

        # Where <LS> = 'E1' <DATEPLACED> should be <= <DECOM> of first episode in <PERIODOFCARE> with <LS> = 'E1'
        mask = merged["DATEPLACED"] > merged["DECOM"]

        # error locations
        epserrorlocs = merged.loc[mask, "epsindex"]
        paerrorlocs = merged.loc[mask, "paindex"]

        return {
            "Episodes": epserrorlocs.tolist(),
            "PlacedAdoption": paerrorlocs.unique().tolist(),
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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 8], "PlacedAdoption": [0, 3]}
