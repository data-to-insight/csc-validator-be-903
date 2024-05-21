import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW08STG2",
    message="A new social worker episode has started, but the previous episode has not ended.",
    affected_fields=["SW_DEC"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        df["SW_DECOM"] = pd.to_datetime(
            df["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        df["SW_DEC"] = pd.to_datetime(df["SW_DEC"], format="%d/%m/%Y", errors="coerce")

        df["SW_DECOM"] = df["SW_DECOM"].fillna(
            "01/01/1901"
        )  # Watch for potential future issues

        df["SW_DECOM"] = df["SW_DECOM"].replace("01/01/1901", pd.NA)

        last_episodes = (
            df.sort_values("SW_DECOM").reset_index().groupby(["CHILD"])["index"].last()
        )
        ended_episodes_df = df.loc[~df.index.isin(last_episodes)]

        ended_episodes_df = ended_episodes_df[
            (ended_episodes_df["SW_DEC"].isna())
            & ended_episodes_df["CHILD"].notna()
            & ended_episodes_df["SW_DECOM"].notna()
        ]
        mask = ended_episodes_df.index.tolist()

        return {"SWEpisodes": mask}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "SW_DECOM": "01/06/2020",
                "SW_DEC": "04/06/2020",
            },  # 0
            {
                "CHILD": "111",
                "SW_DECOM": "05/06/2020",
                "SW_DEC": "06/06/2020",
            },  # 1
            {
                "CHILD": "111",
                "SW_DECOM": "06/06/2020",
                "SW_DEC": "08/06/2020",
            },  # 2
            {
                "CHILD": "111",
                "SW_DECOM": "08/06/2020",
                "SW_DEC": "05/06/2020",
            },  # 3
            {
                "CHILD": "222",
                "SW_DECOM": "05/06/2020",
                "SW_DEC": "06/06/2020",
            },  # 4
            {
                "CHILD": "333",
                "SW_DECOM": "06/06/2020",
                "SW_DEC": pd.NA,
            },  # 5   Fails because an episode starts after this one
            {
                "CHILD": "333",
                "SW_DECOM": "07/06/2020",
                "SW_DEC": "08/06/2020",
            },  # 6
            {
                "CHILD": "444",
                "SW_DECOM": "08/06/2020",
                "SW_DEC": "09/06/2020",
            },  # 7
            {
                "CHILD": "444",
                "SW_DECOM": "09/06/2020",
                "SW_DEC": "10/06/2020",
            },  # 8
            {
                "CHILD": "444",
                "SW_DECOM": "15/06/2020",
                "SW_DEC": pd.NA,
            },  # 9
            {
                "CHILD": "555",
                "SW_DECOM": "11/06/2020",
                "SW_DEC": "12/06/2020",
            },  # 10
            {
                "CHILD": "6666",
                "SW_DECOM": "12/06/2020",
                "SW_DEC": "13/06/2020",
            },  # 11
            {
                "CHILD": "6666",
                "SW_DECOM": "13/06/2020",
                "SW_DEC": "14/06/2020",
            },  # 12
            {
                "CHILD": "6666",
                "SW_DECOM": "14/06/2020",
                "SW_DEC": pd.NA,
            },  # 13  Fails because an episode starts after this one
            {
                "CHILD": "6666",
                "SW_DECOM": "15/06/2020",
                "SW_DEC": "16/06/2020",
            },  # 14
            {
                "CHILD": "77777",
                "SW_DECOM": "16/06/2020",
                "SW_DEC": "17/06/2020",
            },  # 15
            {
                "CHILD": "77777",
                "SW_DECOM": "17/06/2020",
                "SW_DEC": "18/06/2020",
            },  # 16
            {
                "CHILD": "77777",
                "SW_DECOM": "18/06/2020",
                "SW_DEC": pd.NA,
            },  # 17
            {
                "CHILD": "999",
                "SW_DECOM": "31/06/2020",
                "SW_DEC": pd.NA,
            },  # 18   Nonsense date, but should pass
            {
                "CHILD": "123",
                "SW_DECOM": pd.NA,
                "SW_DEC": pd.NA,
            },  # 19   Nonsense dates, but should pass
            {
                "CHILD": pd.NA,
                "SW_DECOM": pd.NA,
                "SW_DEC": pd.NA,
            },  # 20   Nonsense, but should pass
        ]
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [5, 13]}
