import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="336",
        description="Child does not have a foster placement immediately prior to being placed for adoption.",
        affected_fields=["PLACE"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            place_code_list = ["A3", "A4"]
            prev_code_list = [
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

            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            # new column that contains place of previous episode

            sorted_and_grouped_eps = episodes.sort_values("DECOM").groupby("CHILD")

            episodes["PLACE_prev"] = sorted_and_grouped_eps["PLACE"].shift(1)
            episodes["is_first_episode"] = False
            episodes.loc[
                sorted_and_grouped_eps["DECOM"].idxmin(), "is_first_episode"
            ] = True

            # Where <PL> = 'A3' or 'A5' previous episode <PL> must be one of:
            # ('A3'; 'A4'; 'A5'; 'A6'; 'U1', 'U2', 'U3', 'U4', 'U5' or 'U6')
            mask = (
                (episodes["PLACE"].isin(place_code_list))
                & ~episodes["PLACE_prev"].isin(prev_code_list)
                & ~episodes["is_first_episode"]  # omit first eps, as prev_PLACE is NaN
            )

            # error locations
            error_locs = episodes.index[mask]
            return {"Episodes": error_locs.tolist()}

    return error, _validate


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
