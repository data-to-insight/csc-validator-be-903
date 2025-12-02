import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="707",
    message="Child ceased to be looked after but there is a DoLO without an end date.",
    affected_fields=["DOLO_END"],
    tables=["DoLo", "EPISODES"],
)
def validate(dfs):
    # Uses the logic from 577 which is the same rule but for missing
    if "Episodes" not in dfs or "DoLo" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        dolo = dfs["DoLo"]

        episodes["original_index"] = episodes.index

        # put dates in appropriate format.
        dolo["DOLO_END"] = pd.to_datetime(
            dolo["DOLO_END"], format="%d/%m/%Y", errors="coerce"
        )
        dolo["DOLO_START"] = pd.to_datetime(
            dolo["DOLO_START"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # filter data based on provided conditions.
        dolo = dolo[dolo["DOLO_START"].notna()].copy()
        episodes = episodes.dropna(subset=["DECOM"])

        # create period of care blocks
        episodes = episodes.sort_values(["CHILD", "DECOM"])

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
        pocs = pd.DataFrame()
        pocs[["CHILD", "poc_DECOM"]] = episodes.groupby("period_id")[
            ["CHILD", "DECOM"]
        ].first()
        pocs["poc_DEC"] = episodes.groupby("period_id")["DEC"].nth(-1)

        # prepare to merge
        dolo["index_dolo"] = dolo.index

        pocs = pocs.merge(dolo, on="CHILD", how="right", suffixes=["_eps", "_dolo"])
        # poc : period of care
        pocs["out_of_poc"] = (
            # (a) POC is over, but dolo ep is ongoing:
            (
                pocs["DOLO_START"].notna()
                & pocs["DOLO_END"].isna()
                & pocs["poc_DEC"].notna()
            )
            # (b) Ongoing dolo ep, but started before POC:
            | (pocs["DOLO_END"].isna() & (pocs["DOLO_START"] < pocs["poc_DECOM"]))
            # (c) dolo ep ends after POC:
            | (pocs["DOLO_END"] > pocs["poc_DEC"])
            # (d) dolog ep ends before POC:
            | (pocs["DOLO_END"] < pocs["poc_DECOM"])
            # (e?) Starts during a previous poc??? (row 12 of dolo table in testvalidate_577)
        )

        # Drop rows where child was not present in 'dolo' table.
        pocs = pocs[pocs["index_dolo"].notna()]

        mask = pocs.groupby("index_dolo")["out_of_poc"].transform("min")
        dolo_error_locs = pocs.loc[mask, "index_dolo"].astype(int).unique().tolist()

        return {"DoLo": dolo_error_locs}


def test_validate():
    import pandas as pd

    fake_data_dolo = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "DOLO_START": "01/01/1981",
                "DOLO_END": pd.NA,
            },  # 0
            {
                "CHILD": "2",
                "DOLO_START": "01/01/1981",
                "DOLO_END": "02/06/2020",
            },  # 1
            {
                "CHILD": "3",
                "DOLO_START": "01/01/1981",
                "DOLO_END": "03/06/2022",
            },  # 2 fail: fail1 fail2
            {
                "CHILD": "3",
                "DOLO_START": "01/01/1981",
                "DOLO_END": "03/06/2020",
            },  # 3 pass: fail with the first, pass with the second
            {
                "CHILD": "4",
                "DOLO_START": "01/01/1981",
                "DOLO_END": "04/06/2020",
            },  # 4
            {
                "CHILD": "5",
                "DOLO_START": "01/01/1981",
                "DOLO_END": "01/01/1982",
            },  # 5 passes with full period of care DECOM-DEC (7/8) and 9
            {
                "CHILD": "5",
                "DOLO_START": "01/01/1981",
                "DOLO_END": "01/01/2000",
            },  # 6 pass: fails with first set of episodes(7/8 poc), but passes with next period of care (9)
            {
                "CHILD": "6",
                "DOLO_START": "01/01/1981",
                "DOLO_END": "01/01/1981",
            },  # 7 fail when compared with DECOM
            {
                "CHILD": "7",
                "DOLO_START": pd.NA,
                "DOLO_END": "01/01/1981",
            },  # 8 ignore fail: MIS_START is NaN
            {
                "CHILD": "8",
                "DOLO_START": "01/01/1981",
                "DOLO_END": pd.NA,
            },  # 9 fail: MIS_END is nan
            {
                "CHILD": "9",
                "DOLO_START": "01/01/2020",
                "DOLO_END": pd.NA,
            },  # 10 fail: MIS_END is nan
            {
                "CHILD": "9",
                "DOLO_START": "01/01/2021",
                "DOLO_END": pd.NA,
            },  # 11 pass: ongoing mis-ep during ongoing poc
            {
                "CHILD": "9",
                "DOLO_START": "04/06/2020",
                "DOLO_END": "04/06/2021",
            },  # 12 pass: ends during a poc (?!)
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
            },  # 4
            {
                "CHILD": "3",
                "DECOM": "01/01/2021",
                "DEC": "05/10/2021",
                "LS": "V3",
                "REC": "kk",
            },  # 5
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
                "REC": "xx",
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
                "CHILD": "7",
                "DECOM": "01/04/1983",
                "DEC": "04/06/2020",
                "LS": "o",
                "REC": "kk",
            },  # 11
            {
                "CHILD": "8",
                "DECOM": "01/04/1983",
                "DEC": "04/06/2020",
                "LS": "o",
                "REC": "xx",
            },  # 12
            {
                "CHILD": "9",
                "DECOM": "01/01/2020",
                "DEC": "04/06/2020",
                "LS": "o",
                "REC": "<--",
            },  # 10
            {
                "CHILD": "9",
                "DECOM": "04/06/2020",
                "DEC": "11/08/2020",
                "LS": "o",
                "REC": "-",
            },  # 10
            {
                "CHILD": "9",
                "DECOM": "11/08/2020",
                "DEC": "01/12/2020",
                "LS": "o",
                "REC": "-->",
            },  # 10
            {
                "CHILD": "9",
                "DECOM": "22/12/2020",
                "DEC": "25/12/2020",
                "LS": "o",
                "REC": "<->",
            },  # 10
            {
                "CHILD": "9",
                "DECOM": "01/01/2021",
                "DEC": "22/02/2021",
                "LS": "o",
                "REC": "<--",
            },  # 10
            {
                "CHILD": "9",
                "DECOM": "22/02/2021",
                "DEC": "08/08/2021",
                "LS": "V3",
                "REC": "-",
            },  # 10
            {
                "CHILD": "9",
                "DECOM": "08/08/2021",
                "DEC": pd.NA,
                "LS": "o",
                "REC": "--o",
            },  # 10
        ]
    )

    fake_dfs = {"DoLo": fake_data_dolo, "Episodes": fake_data_eps}

    result = validate(fake_dfs)

    assert result == {"DoLo": [0, 1, 2, 7, 9, 10]}
