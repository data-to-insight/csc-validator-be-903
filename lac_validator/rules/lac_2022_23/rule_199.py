import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="199",
    message="Episode information shows child has been previously adopted from care. "
    "[NOTE: This only tests the current and previous year data loaded into the tool]",
    affected_fields=["CHILD"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["currentyearindex"] = episodes.index

        if "Episodeslast" in dfs:
            episodeslast = dfs["Episodeslast"]
            episodes = pd.concat([episodes, episodeslast], axis=0)

    episodes["isad"] = episodes["REC"].isin(["E11", "E12"]).astype(int)
    episodes["DECOM"] = pd.todatetime(
        episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
    )

    episodes = episodes.dropna(subset=["DECOM"]).sortvalues("DECOM")

    episodes["adstod8"] = episodes.groupby("CHILD")["isad"].cumsum()
    errormask = (
        episodes["adstod8"] > 0
    ) & ~(  # error if there have been any adoption episodes to date...
        (episodes["adstod8"]) == 1 & episodes["REC"].isin(["E11", "E12"])
    )  # ...unless this is the first

    errorlocations = (
        episodes.loc[errormask, "currentyearindex"]
        .dropna()
        .sortvalues()
        .astype(int)
        .tolist()
    )

    return {"Episodes": errorlocations}


def test_validate():
    import pandas as pd

    fake_data_199_episodes_last = pd.DataFrame(
        [
            {"CHILD": "101", "DECOM": "15/06/2016", "DEC": "20/12/2020", "REC": "E11"},
            {"CHILD": "102", "DECOM": "08/10/2017", "DEC": "03/03/2018", "REC": "E11"},
            {"CHILD": "102", "DECOM": "06/03/2018", "DEC": "12/08/2020", "REC": "E4a"},
            {"CHILD": "103", "DECOM": "11/05/2015", "DEC": "07/04/2019", "REC": "E12"},
            {"CHILD": "104", "DECOM": "26/11/2017", "DEC": "19/07/2020", "REC": "E12"},
            {"CHILD": "107", "DECOM": "26/11/2017", "DEC": pd.NA, "REC": "E12"},
        ]
    )

    fake_data_199_episodes = pd.DataFrame(
        [
            {
                "CHILD": "104",
                "DECOM": "19/07/2020",
                "DEC": "02/03/2021",
                "REC": "E13",
            },  # 0: Pass -> Fail
            {
                "CHILD": "103",
                "DECOM": "16/04/2020",
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 1: Pass -> Fail
            {
                "CHILD": "103",
                "DECOM": "16/04/2020",
                "DEC": pd.NA,
                "REC": "oo",
            },  # 2: Pass -> Fail
            {
                "CHILD": "105",
                "DECOM": "02/12/2021",
                "DEC": "03/12/2021",
                "REC": "X1",
            },  # 3: Pass
            {
                "CHILD": "105",
                "DECOM": "03/12/2021",
                "DEC": "04/12/2021",
                "REC": "E11",
            },  # 4:Pass
            {
                "CHILD": "105",
                "DECOM": "03/12/2022",
                "DEC": "04/12/2022",
                "REC": "E11",
            },  # 5: Fail
            {
                "CHILD": "105",
                "DECOM": "12/12/2021",
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 6: Fail
            {
                "CHILD": "107",
                "DECOM": "04/12/2021",
                "DEC": pd.NA,
                "REC": "XXX",
            },  # 7: Fail
            {
                "CHILD": "107",
                "DECOM": "26/11/2017",
                "DEC": "04/12/2021",
                "REC": "E12",
            },  # 8: Pass
        ]
    )
    error_defn, error_func = validate()

    fake_dfs = {"Episodes": fake_data_199_episodes.copy()}
    result = error_func(fake_dfs)
    assert result == {"Episodes": [5, 6, 7]}

    fake_dfs = {
        "Episodes": fake_data_199_episodes,
        "Episodes_last": fake_data_199_episodes_last,
    }
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 1, 2, 5, 6, 7]}
