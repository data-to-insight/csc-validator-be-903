import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="142",
    message="A new episode has started, but the previous episode has not ended.",
    affected_fields=["DEC", "REC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        df["DECOM"] = pd.todatetime(df["DECOM"], format="%d/%m/%Y", errors="coerce")
        df["DEC"] = pd.todatetime(df["DEC"], format="%d/%m/%Y", errors="coerce")

        df["DECOM"] = df["DECOM"].fillna(
            "01/01/1901"
        )  # Watch for potential future issues

        df["DECOM"] = df["DECOM"].replace("01/01/1901", pd.NA)

        lastepisodes = (
            df.sortvalues("DECOM").resetindex().groupby(["CHILD"])["index"].last()
        )
        endedepisodesdf = df.loc[~df.index.isin(lastepisodes)]

        endedepisodesdf = endedepisodesdf[
            (endedepisodesdf["DEC"].isna() | endedepisodesdf["REC"].isna())
            & endedepisodesdf["CHILD"].notna()
            & endedepisodesdf["DECOM"].notna()
        ]
        mask = endedepisodesdf.index.tolist()

        return {"Episodes": mask}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
                "REC": "X1",
            },  # 0
            {
                "CHILD": "111",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
                "REC": pd.NA,
            },  # 1  Fails
            {
                "CHILD": "111",
                "DECOM": "06/06/2020",
                "DEC": "08/06/2020",
                "REC": "X1",
            },  # 2
            {
                "CHILD": "111",
                "DECOM": "08/06/2020",
                "DEC": "05/06/2020",
                "REC": "X1",
            },  # 3
            {
                "CHILD": "222",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
                "REC": pd.NA,
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "06/06/2020",
                "DEC": pd.NA,
                "REC": "E11",
            },  # 5   Fails
            {"CHILD": "333", "DECOM": "07/06/2020", "DEC": pd.NA, "REC": pd.NA},  # 6
            {
                "CHILD": "444",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
                "REC": "X1",
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "09/06/2020",
                "DEC": "10/06/2020",
                "REC": "E11",
            },  # 8
            {"CHILD": "444", "DECOM": "15/06/2020", "DEC": pd.NA, "REC": pd.NA},  # 9
            {
                "CHILD": "555",
                "DECOM": "11/06/2020",
                "DEC": "12/06/2020",
                "REC": "X1",
            },  # 10
            {
                "CHILD": "6666",
                "DECOM": "12/06/2020",
                "DEC": "13/06/2020",
                "REC": "X1",
            },  # 11
            {
                "CHILD": "6666",
                "DECOM": "13/06/2020",
                "DEC": "14/06/2020",
                "REC": "X1",
            },  # 12
            {
                "CHILD": "6666",
                "DECOM": "14/06/2020",
                "DEC": pd.NA,
                "REC": "X1",
            },  # 13  Fails
            {
                "CHILD": "6666",
                "DECOM": "15/06/2020",
                "DEC": "16/06/2020",
                "REC": "X1",
            },  # 14
            {
                "CHILD": "77777",
                "DECOM": "16/06/2020",
                "DEC": "17/06/2020",
                "REC": "X1",
            },  # 15
            {
                "CHILD": "77777",
                "DECOM": "17/06/2020",
                "DEC": "18/06/2020",
                "REC": "X1",
            },  # 16
            {"CHILD": "77777", "DECOM": "18/06/2020", "DEC": pd.NA, "REC": "X1"},  # 17
            {
                "CHILD": "999",
                "DECOM": "31/06/2020",
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 18   Nonsense date, but should pass
            {
                "CHILD": "123",
                "DECOM": pd.NA,
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 19   Nonsense dates, but should pass
            {
                "CHILD": pd.NA,
                "DECOM": pd.NA,
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 20   Nonsense, but should pass
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 5, 13]}
