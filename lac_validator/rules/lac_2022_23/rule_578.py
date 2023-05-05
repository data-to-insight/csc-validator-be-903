import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="578",
    message="The date that the child started to be missing is after the child ceased to be looked after.",
    affected_fields=["MIS_START"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Missing" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        missing = dfs["Missing"]

        episodes["originalindex"] = episodes.index

        # convert dates
        episodes["DEC"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        missing["MISSTART"] = pd.todatetime(
            missing["MISSTART"], format="%d/%m/%Y", errors="coerce"
        )

        # create period of care blocks
        episodes = episodes.sortvalues(["CHILD", "DECOM"])
        episodes = episodes.dropna(subset=["DECOM"])

        episodes["index"] = pd.RangeIndex(0, len(episodes))
        episodes["index+1"] = episodes["index"] + 1
        episodes = episodes.merge(
            episodes,
            lefton="index",
            righton="index+1",
            how="left",
            suffixes=[None, "prev"],
        )
        episodes = episodes[
            [
                "originalindex",
                "DECOM",
                "DEC",
                "DECprev",
                "CHILD",
                "CHILDprev",
                "LS",
            ]
        ]

        episodes["newperiod"] = (episodes["DECOM"] > episodes["DECprev"]) | (
            episodes["CHILD"] != episodes["CHILDprev"]
        )
        episodes["periodid"] = episodes["newperiod"].astype(int).cumsum()

        # allocate the same DECOM (min) and DEC (max) to all episodes in a period of care.
        episodes["pocDECOM"] = episodes.groupby("periodid")["DECOM"].transform("min")
        episodes["pocDEC"] = episodes.groupby("periodid")["DEC"].transform("max")

        # prepare to merge
        missing["indexing"] = missing.index

        pocs = pd.DataFrame()
        pocs[["CHILD", "pocDECOM"]] = episodes.groupby("periodid")[
            ["CHILD", "DECOM"]
        ].first()
        pocs["pocDEC"] = episodes.groupby("periodid")["DEC"].nth(-1)

        pocs = pocs.merge(missing, on="CHILD", how="right", suffixes=["eps", "ing"])
        # If <MISSTART> >=DEC, then no missing/away from placement information should be recorded
        pocs["outofpoc"] = (pocs["MISSTART"] < pocs["pocDECOM"]) | (
            (pocs["MISSTART"] > pocs["pocDEC"]) & pocs["pocDEC"].notna()
        )

        # Drop rows where child was not present in 'Missing' table.
        pocs = pocs[pocs["indexing"].notna()]

        mask = pocs.groupby("indexing")["outofpoc"].transform("min")
        misserrorlocs = pocs.loc[mask, "indexing"].astype(int).unique().tolist()

        # In this case it is not necessary to flag the DEC or DECOM that value because that same DEC or DECOM value might have passed with other values of MISSTART. Flagging the DECOM/ DEC value is not specific enough to be helpful to the user.
        return {"Missing": misserrorlocs}


def test_validate():
    import pandas as pd

    fake_data_mis = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "MIS_START": "01/06/2020",
            },  # 0 fail
            {
                "CHILD": "2",
                "MIS_START": "02/06/2020",
            },  # 1 fail
            {
                "CHILD": "3",
                "MIS_START": "03/06/2022",
            },  # 2 fail: fail1 fail2
            {
                "CHILD": "3",
                "MIS_START": "03/06/2020",
            },  # 3 fail with the first, pass with the second : pass
            {
                "CHILD": "4",
                "MIS_START": "04/06/2020",
            },  # 4
            {
                "CHILD": "5",
                "MIS_START": "01/01/1982",
            },  # 5 passes with full period of care DECOM-DEC (7/8) and 9
            {
                "CHILD": "5",
                "MIS_START": "01/01/2000",
            },  # 6 pass: fails with first set of episodes(7/8 poc), but passes with next period of care (9)
            {
                "CHILD": "6",
                "MIS_START": "01/01/1981",
            },  # 7 fail when compared with DECOM
            {
                "CHILD": "77",
                "MIS_START": "01/01/1981",
            },  # 8 pass
            {
                "CHILD": "8888",
                "MIS_START": "01/01/2049",
            },  # 8 pass
        ]
    )
    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "DECOM": "01/04/1977",
                "DEC": "31/03/1981",
                "LS": "o",
                "REC": "X1",
            },  # 0
            {
                "CHILD": "2",
                "DECOM": "01/04/1979",
                "DEC": "30/03/1981",
                "LS": "o",
                "REC": pd.NA,
            },  # 1
            {
                "CHILD": "88",
                "DECOM": "01/05/1980",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "xx",
            },  # 2
            {
                "CHILD": "3",
                "DECOM": "01/04/1980",
                "DEC": "01/01/1981",
                "LS": "V3",
                "REC": "kk",
            },  # 3
            {
                "CHILD": "3",
                "DECOM": "01/04/2020",
                "DEC": "01/01/2021",
                "LS": "V3",
                "REC": "kk",
            },  # 4 --not poc
            {
                "CHILD": "3",
                "DECOM": "01/01/2021",
                "DEC": "05/10/2021",
                "LS": "V3",
                "REC": "kk",
            },  # 5 due to LS value--
            {
                "CHILD": "4",
                "DECOM": "01/04/1981",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "!!",
            },  # 6
            {
                "CHILD": "5",
                "DECOM": "01/04/1978",
                "DEC": "01/01/1981",
                "LS": "o",
                "REC": "X1",
            },  # 7 --poc start
            {
                "CHILD": "5",
                "DECOM": "01/01/1981",
                "DEC": "01/01/1990",
                "LS": "o",
                "REC": "xx",
            },  # 8  poc end--
            {
                "CHILD": "5",
                "DECOM": "01/04/1983",
                "DEC": "04/06/2020",
                "LS": "o",
                "REC": "kk",
            },  # 9
            {
                "CHILD": "6",
                "DECOM": "01/04/1983",
                "DEC": "04/06/2020",
                "LS": "o",
                "REC": "kk",
            },  # 10
            {
                "CHILD": "8888",
                "DECOM": "01/04/1983",
                "DEC": "04/06/2020",
                "LS": "o",
                "REC": "kk",
            },  # 10
            {
                "CHILD": "8888",
                "DECOM": "04/06/2020",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "kk",
            },  # 10
        ]
    )

    fake_dfs = {"Episodes": fake_data_eps, "Missing": fake_data_mis}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Missing": [0, 1, 2, 7]}
