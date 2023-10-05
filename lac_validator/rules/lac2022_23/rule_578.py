import pandas as pd

from lac_validator.rule_engine import rule_definition


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

        episodes["original_index"] = episodes.index

        # convert dates
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        missing["MIS_START"] = pd.to_datetime(
            missing["MIS_START"], format="%d/%m/%Y", errors="coerce"
        )

        # create period of care blocks
        episodes = episodes.sort_values(["CHILD", "DECOM"])
        episodes = episodes.dropna(subset=["DECOM"])

        episodes["index"] = pd.RangeIndex(0, len(episodes))
        episodes["index+1"] = episodes["index"] + 1
        episodes = episodes.merge(
            episodes,
            left_on="index",
            right_on="index+1",
            how="left",
            suffixes=[None, "_prev"],
        )
        episodes = episodes[
            [
                "original_index",
                "DECOM",
                "DEC",
                "DEC_prev",
                "CHILD",
                "CHILD_prev",
                "LS",
            ]
        ]

        episodes["new_period"] = (episodes["DECOM"] > episodes["DEC_prev"]) | (
            episodes["CHILD"] != episodes["CHILD_prev"]
        )
        episodes["period_id"] = episodes["new_period"].astype(int).cumsum()

        # allocate the same DECOM (min) and DEC (max) to all episodes in a period of care.
        episodes["poc_DECOM"] = episodes.groupby("period_id")["DECOM"].transform("min")
        episodes["poc_DEC"] = episodes.groupby("period_id")["DEC"].transform("max")

        # prepare to merge
        missing["index_ing"] = missing.index

        pocs = pd.DataFrame()
        pocs[["CHILD", "poc_DECOM"]] = episodes.groupby("period_id")[
            ["CHILD", "DECOM"]
        ].first()
        pocs["poc_DEC"] = episodes.groupby("period_id")["DEC"].nth(-1)

        pocs = pocs.merge(missing, on="CHILD", how="right", suffixes=["_eps", "_ing"])
        # If <MIS_START> >=DEC, then no missing/away from placement information should be recorded
        pocs["out_of_poc"] = (pocs["MIS_START"] < pocs["poc_DECOM"]) | (
            (pocs["MIS_START"] > pocs["poc_DEC"]) & pocs["poc_DEC"].notna()
        )

        # Drop rows where child was not present in 'Missing' table.
        pocs = pocs[pocs["index_ing"].notna()]

        mask = pocs.groupby("index_ing")["out_of_poc"].transform("min")
        miss_error_locs = pocs.loc[mask, "index_ing"].astype(int).unique().tolist()

        # In this case it is not necessary to flag the DEC or DECOM that value because that same DEC or DECOM value might have passed with other values of MIS_START. Flagging the DECOM/ DEC value is not specific enough to be helpful to the user.
        return {"Missing": miss_error_locs}


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

    result = validate(fake_dfs)

    assert result == {"Missing": [0, 1, 2, 7]}
