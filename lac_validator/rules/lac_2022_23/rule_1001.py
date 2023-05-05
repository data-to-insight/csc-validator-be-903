import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="1001",
    message="The episodes recorded for this young person suggest they are not a relevant or a former relevant "
    "child and therefore should not have care leaver information completed. "
    "[NOTE: This tool can only test the current and previous year data loaded into the tool - this "
    "check may generate false positives if a child had episodes prior to last year's collection.]",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    # requiring 'Episodeslast' to reduce false positive rate, though more could be done
    if any(
        tablename not in dfs
        for tablename in ("Episodes", "OC3", "Header", "Episodeslast")
    ):
        return {}
    elif any(
        len(dfs[tablename]) == 0
        for tablename in ("Episodes", "OC3", "Header", "Episodeslast")
    ):
        return {}
    else:
        currenteps = dfs["Episodes"]
        preveps = dfs["Episodeslast"]
        oc3 = dfs["OC3"]
        header = dfs["Header"]

        collectionend = dfs["metadata"]["collectionend"]
        collectionend = pd.todatetime(collectionend, format="%d/%m/%Y", errors="coerce")

        episodes = pd.concat([currenteps, preveps], axis=0)
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        episodes.dropduplicates(subset=["CHILD", "DECOM"])

        header["DOB"] = pd.todatetime(header["DOB"], format="%d/%m/%Y", errors="coerce")
        header = header[header["DOB"].notnull()]
        header["DOB14"] = header["DOB"] + pd.DateOffset(years=14)
        header["DOB16"] = header["DOB"] + pd.DateOffset(years=16)

        # Drop children who are over 20 years old at collection end,
        # as we would not expect to see sufficient episodes in the past 2 years of data
        header = header[header["DOB"] + pd.DateOffset(years=20) > collectionend]

        # this should drop any episodes duplicated between years.
        # keep='first' should drop prev. year's missing DEC
        episodes = episodes.sortvalues("DEC").dropduplicates(
            ["CHILD", "DECOM"], keep="first"
        )

        # fill in missing final DECs with the collection year's end date
        missinglastDECs = (
            episodes.index.isin(episodes.groupby("CHILD")["DECOM"].idxmax())
            & episodes["DEC"].isna()
        )
        episodes.loc[missinglastDECs, "DEC"] = collectionend

        # Work out how long child has been in care since 14th and 16th birthdays.
        episodesmerged = (
            episodes.resetindex()
            .merge(
                header[["CHILD", "DOB", "DOB14", "DOB16"]],
                how="inner",
                on=["CHILD"],
                suffixes=("", "header"),
                indicator=True,
            )
            .setindex("index")
        )

        # Drop all episodes with V3/V4 legal status
        v3v4ls = episodesmerged["LS"].str.upper().isin(["V3", "V4"])
        indexv3v4ls = episodesmerged.loc[v3v4ls].index
        episodesmerged.drop(indexv3v4ls, inplace=True)

        if len(episodesmerged) == 0:
            return {"OC3": []}

        episodesmerged["DECOM14"] = episodesmerged[["DECOM", "DOB14"]].max(axis=1)
        episodesmerged["DECOM16"] = episodesmerged[["DECOM", "DOB16"]].max(axis=1)

        episodesmerged["DURATION14"] = (
            episodesmerged["DEC"] - episodesmerged["DECOM14"]
        ).dt.days.clip(lower=0)
        episodesmerged["DURATION16"] = (
            episodesmerged["DEC"] - episodesmerged["DECOM16"]
        ).dt.days.clip(lower=0)

        episodesmerged["TOTAL14"] = episodesmerged.groupby("CHILD")[
            "DURATION14"
        ].transform("sum")
        episodesmerged["TOTAL16"] = episodesmerged.groupby("CHILD")[
            "DURATION16"
        ].transform("sum")

        totals = episodesmerged[["CHILD", "TOTAL14", "TOTAL16"]].dropduplicates("CHILD")

        oc3 = oc3.merge(totals, how="left")

        # print(episodesmerged[['CHILD', 'DOB', 'DURATION14', 'TOTAL14', 'DURATION16', 'TOTAL16']])
        # print(episodesmerged[['CHILD', 'DOB', 'LS', 'REC', 'EVERADOPTED', 'DURATION V3/V4']])

        hascareafter14 = oc3["TOTAL14"] >= 91
        hascareafter16 = oc3["TOTAL16"] >= 1

        validcareleaver = hascareafter14 & hascareafter16

        # Find out if child has been adopted
        episodesmax = episodes.groupby("CHILD")["DECOM"].idxmax()
        episodesmax = episodes.loc[episodesmax]
        episodesadopted = episodesmax[
            episodesmax["REC"].str.upper().isin(["E11", "E12"])
        ]
        adopted = oc3["CHILD"].isin(episodesadopted["CHILD"])

        errormask = adopted | ~validcareleaver

        validationerrorlocations = oc3.index[errormask]

        return {"OC3": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    # DOB always 01/01/2000
    # next to each episode, approx days in each age bracket is listed like so:      under 14  :  14-16  :  over 16
    eps = pd.DataFrame(
        [
            # [0] - PASS: more than 91 relevant days
            {
                "CHILD": "1111",
                "LS": "C2",
                "DECOM": "01/01/2014",
                "DEC": "01/02/2014",
                "REC": "o",
            },  # :30:
            {
                "CHILD": "1111",
                "LS": "C2",
                "DECOM": "01/02/2015",
                "DEC": "01/06/2015",
                "REC": "o",
            },  # :120:
            {
                "CHILD": "1111",
                "LS": "C2",
                "DECOM": "01/01/2016",
                "DEC": "01/02/2016",
                "REC": "o",
            },  # ::1
            # [1] - FAIL: less than 91 days
            {
                "CHILD": "2222",
                "LS": "C2",
                "DECOM": "01/01/2010",
                "DEC": "01/02/2014",
                "REC": "o",
            },  # :30:
            {
                "CHILD": "2222",
                "LS": "C2",
                "DECOM": "01/01/2010",
                "DEC": pd.NA,
                "REC": "o",
            },  # Duplicate DECOM, missing
            # DEC - should get dropped
            {
                "CHILD": "2222",
                "LS": "C2",
                "DECOM": "25/12/2015",
                "DEC": "01/02/2016",
                "REC": "o",
            },  # :7:30
            # [2] - FAIL: more than 91 days but not after 14th bday
            {
                "CHILD": "3333",
                "LS": "C2",
                "DECOM": "01/01/2010",
                "DEC": "01/03/2014",
                "REC": "o",
            },  # 120:60:
            {
                "CHILD": "3333",
                "LS": "C2",
                "DECOM": "25/12/2015",
                "DEC": "04/01/2016",
                "REC": "o",
            },  # :7:3
            # [3] - PASS: more than 91 days, all after 16th bday
            {
                "CHILD": "4444",
                "LS": "C2",
                "DECOM": "01/01/2016",
                "DEC": "01/02/2016",
                "REC": "o",
            },  # ::30
            {
                "CHILD": "4444",
                "LS": "C2",
                "DECOM": "25/12/2016",
                "DEC": "01/04/2017",
                "REC": "o",
            },  # ::120
            # [-] - PASS: not in OC3
            {
                "CHILD": "5555",
                "LS": "C2",
                "DECOM": "01/01/2010",
                "DEC": "01/05/2012",
                "REC": "o",
            },  # 120:60:
            {
                "CHILD": "5555",
                "LS": "C2",
                "DECOM": "25/12/2015",
                "DEC": "04/01/2016",
                "REC": "o",
            },  # :7:3
            # [4] - FAIL: more than 91 days but none after 16th bday
            {
                "CHILD": "6006",
                "LS": "C2",
                "DECOM": "01/01/2014",
                "DEC": "01/02/2014",
                "REC": "o",
            },  # :30:
            {
                "CHILD": "6006",
                "LS": "C2",
                "DECOM": "01/02/2015",
                "DEC": "01/08/2015",
                "REC": "o",
            },  # :180:
            # [5] - FAIL: enough days but including V3 episode
            {
                "CHILD": "7777",
                "LS": "C2",
                "DECOM": "01/01/2013",
                "DEC": "01/03/2014",
                "REC": "o",
            },  # 365:60:
            {
                "CHILD": "7777",
                "LS": "V3",
                "DECOM": "01/01/2015",
                "DEC": "01/02/2015",
                "REC": "o",
            },  # :30: (doesnt count)
            {
                "CHILD": "7777",
                "LS": "C2",
                "DECOM": "25/12/2015",
                "DEC": "04/01/2016",
                "REC": "o",
            },  # :7:3
            # [6] - FAIL:  more than 91 days but final REC E11/E12
            {
                "CHILD": "8888",
                "LS": "C2",
                "DECOM": "01/01/2014",
                "DEC": "01/02/2014",
                "REC": "o",
            },  # :30:
            {
                "CHILD": "8888",
                "LS": "C2",
                "DECOM": "01/02/2015",
                "DEC": "01/08/2015",
                "REC": "o",
            },  # :180:
            {
                "CHILD": "8888",
                "LS": "C2",
                "DECOM": "01/02/2016",
                "DEC": "01/03/2016",
                "REC": "o",
            },  # ::30
            {
                "CHILD": "8888",
                "LS": "C2",
                "DECOM": "01/03/2017",
                "DEC": "01/05/2017",
                "REC": "E11",
            },  # ::60 but E11
            # [8] - PASS: more than 91 days if missing DEC filled in
            {
                "CHILD": "9999",
                "LS": "C2",
                "DECOM": "01/01/2010",
                "DEC": "01/05/2012",
                "REC": "o",
            },  # 120:60:
            {
                "CHILD": "9999",
                "LS": "C2",
                "DECOM": "01/06/2017",
                "DEC": pd.NA,
                "REC": "o",
            },  # :40:120
        ]
    )

    metadata = {"collection_end": "01/10/2017"}

    # Split episodes into current and previous year dataframes
    eps["DECOM_dt"] = pd.to_datetime(eps["DECOM"], format="%d/%m/%Y", errors="coerce")
    first_ep_per_child = eps.groupby("CHILD")["DECOM_dt"].idxmin()
    prev_eps = eps.loc[first_ep_per_child].copy().drop("DECOM_dt", axis=1)
    current_eps = eps.drop(
        index=first_ep_per_child[:-4], columns="DECOM_dt"
    )  # keep a couple eps in both df's, so we know dups dont break it

    assert (
        len(prev_eps) + len(current_eps) == len(eps) + 4
    ), "(test logic problem) creating current/prev episodes tables didnt work as intended"

    oc3 = pd.DataFrame(
        {
            "CHILD": [
                "1111",
                "2222",
                "3333",
                "4444",
                "6006",
                "7777",
                "8888",
                "9999" "1010101010",
            ],  # '1010101010' not in episodes
        }
    )

    header = pd.DataFrame(
        {
            "CHILD": [
                "1111",
                "2222",
                "3333",
                "4444",
                "6006",
                "7777",
                "8888",
                "1010101010",
            ]
        }
    )
    header["DOB"] = "01/01/2000"

    erro_defn, error_func = validate()

    fake_dfs = {
        "Episodes": current_eps,
        "OC3": oc3,
        "Header": header,
        "Episodes_last": prev_eps,
        "metadata": metadata,
    }
    result = error_func(fake_dfs)
    assert result == {"OC3": [1, 2, 4, 5, 6, 7]}
