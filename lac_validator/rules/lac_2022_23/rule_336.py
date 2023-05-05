import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="336",
    message="Child does not have a foster placement immediately prior to being placed for adoption.",
    affected_fields=["PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placecodelist = ["A3", "A4"]
        prevcodelist = [
            "A3",
            "A4",
            "A5",
            "A6",
            "U1",
            "U2",
            "U3",
            "U4",
            "U5",
            "U6",
        ]

        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        # new column that contains place of previous episode

        sortedandgroupedeps = episodes.sortvalues("DECOM").groupby("CHILD")

        episodes["PLACEprev"] = sortedandgroupedeps["PLACE"].shift(1)
        episodes["isfirstepisode"] = False
        episodes.loc[sortedandgroupedeps["DECOM"].idxmin(), "isfirstepisode"] = True

        # Where <PL> = 'A3' or 'A5' previous episode <PL> must be one of:
        # ('A3'; 'A4'; 'A5'; 'A6'; 'U1', 'U2', 'U3', 'U4', 'U5' or 'U6')
        mask = (
            (episodes["PLACE"].isin(placecodelist))
            & ~episodes["PLACEprev"].isin(prevcodelist)
            & ~episodes["isfirstepisode"]  # omit first eps, as prevPLACE is NaN
        )

        # error locations
        errorlocs = episodes.index[mask]
        return {"Episodes": errorlocs.tolist()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/01/2020",
                "PLACE": "U1",
            },  # 0 ignored no previous episode
            {
                "CHILD": "111",
                "DECOM": "11/01/2020",
                "PLACE": "T1",
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "22/01/2020",
                "PLACE": "A3",
            },  # 2 fail (T1 -> A3)
            {
                "CHILD": "123",
                "DECOM": "11/01/2020",
                "PLACE": "A4",
            },  # 4 pass (U1 -> A4)
            {
                "CHILD": "123",
                "DECOM": "01/01/2020",
                "PLACE": "U1",
            },  # 3
            {
                "CHILD": "333",
                "DECOM": "01/01/2020",
                "PLACE": "U1",
            },  # 5
            {
                "CHILD": "333",
                "DECOM": "22/01/2020",
                "PLACE": "A3",
            },  # 6 fail (T2 -> A3)
            {
                "CHILD": "333",
                "DECOM": "11/01/2020",
                "PLACE": "T2",
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "22/01/2020",
                "PLACE": "A4",
            },  # 8 fail (X1 -> A4)
            {
                "CHILD": "444",
                "DECOM": "11/01/2020",
                "PLACE": "X1",
            },  # 9
            {
                "CHILD": "444",
                "DECOM": "01/01/2020",
                "PLACE": "A3",
            },  # 10 ignored no previous episode
            {
                "CHILD": "666",
                "DECOM": "01/01/2020",
                "PLACE": "A5",
            },  # 11
            {
                "CHILD": "777",
                "DECOM": "11/01/2020",
                "PLACE": "A4",
            },  # 12 fail (null -> A4)
            {
                "CHILD": "777",
                "DECOM": "01/01/2020",
                "PLACE": pd.NA,
            },  # 13
        ]
    )
    fake_dfs = {"Episodes": fake_data_episodes}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [2, 6, 8, 12]}
