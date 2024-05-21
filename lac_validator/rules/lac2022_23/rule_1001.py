import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1001",
    message="The episodes recorded for this young person suggest they are not a relevant or a former relevant "
    "child and therefore should not have care leaver information completed. "
    "[NOTE: This tool can only test the current and previous year data loaded into the tool - this "
    "check may generate false positives if a child had episodes prior to last year's collection.]",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
    tables=["Episodes", "OC3", "HEader", "Episodes_last"],
)
def validate(dfs):
    # requiring 'Episodes_last' to reduce false positive rate, though more could be done
    if any(
        table_name not in dfs
        for table_name in ("Episodes", "OC3", "Header", "Episodes_last")
    ):
        return {}
    elif any(
        len(dfs[table_name]) == 0
        for table_name in ("Episodes", "OC3", "Header", "Episodes_last")
    ):
        return {}
    else:
        current_eps = dfs["Episodes"]
        prev_eps = dfs["Episodes_last"]
        oc3 = dfs["OC3"]
        header = dfs["Header"]

        collection_end = dfs["metadata"]["collection_end"]
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )

        episodes = pd.concat([current_eps, prev_eps], axis=0)
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        episodes.drop_duplicates(subset=["CHILD", "DECOM"])

        header["DOB"] = pd.to_datetime(
            header["DOB"], format="%d/%m/%Y", errors="coerce"
        )
        header = header[header["DOB"].notnull()]
        header["DOB14"] = header["DOB"] + pd.DateOffset(years=14)
        header["DOB16"] = header["DOB"] + pd.DateOffset(years=16)

        # Drop children who are over 20 years old at collection end,
        # as we would not expect to see sufficient episodes in the past 2 years of data
        header = header[header["DOB"] + pd.DateOffset(years=20) > collection_end]

        # this should drop any episodes duplicated between years.
        # keep='first' should drop prev. year's missing DEC
        episodes = episodes.sort_values("DEC").drop_duplicates(
            ["CHILD", "DECOM"], keep="first"
        )

        # fill in missing final DECs with the collection year's end date
        missing_last_DECs = (
            episodes.index.isin(episodes.groupby("CHILD")["DECOM"].idxmax())
            & episodes["DEC"].isna()
        )
        episodes.loc[missing_last_DECs, "DEC"] = collection_end

        # Work out how long child has been in care since 14th and 16th birthdays.
        episodes_merged = (
            episodes.reset_index()
            .merge(
                header[["CHILD", "DOB", "DOB14", "DOB16"]],
                how="inner",
                on=["CHILD"],
                suffixes=("", "_header"),
                indicator=True,
            )
            .set_index("index")
        )

        # Drop all episodes with V3/V4 legal status
        v3v4_ls = episodes_merged["LS"].str.upper().isin(["V3", "V4"])
        index_v3v4_ls = episodes_merged.loc[v3v4_ls].index
        episodes_merged.drop(index_v3v4_ls, inplace=True)

        if len(episodes_merged) == 0:
            return {"OC3": []}

        episodes_merged["DECOM14"] = episodes_merged[["DECOM", "DOB14"]].max(axis=1)
        episodes_merged["DECOM16"] = episodes_merged[["DECOM", "DOB16"]].max(axis=1)

        episodes_merged["DURATION14"] = (
            episodes_merged["DEC"] - episodes_merged["DECOM14"]
        ).dt.days.clip(lower=0)
        episodes_merged["DURATION16"] = (
            episodes_merged["DEC"] - episodes_merged["DECOM16"]
        ).dt.days.clip(lower=0)

        episodes_merged["TOTAL14"] = episodes_merged.groupby("CHILD")[
            "DURATION14"
        ].transform("sum")
        episodes_merged["TOTAL16"] = episodes_merged.groupby("CHILD")[
            "DURATION16"
        ].transform("sum")

        totals = episodes_merged[["CHILD", "TOTAL14", "TOTAL16"]].drop_duplicates(
            "CHILD"
        )

        oc3 = oc3.merge(totals, how="left")

        has_care_after_14 = oc3["TOTAL14"] >= 91
        has_care_after_16 = oc3["TOTAL16"] >= 1

        valid_care_leaver = has_care_after_14 & has_care_after_16

        # Find out if child has been adopted
        episodes_max = episodes.groupby("CHILD")["DECOM"].idxmax()
        episodes_max = episodes.loc[episodes_max]
        episodes_adopted = episodes_max[
            episodes_max["REC"].str.upper().isin(["E11", "E12"])
        ]
        adopted = oc3["CHILD"].isin(episodes_adopted["CHILD"])

        error_mask = adopted | ~valid_care_leaver

        validation_error_locations = oc3.index[error_mask]

        return {"OC3": validation_error_locations.tolist()}


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

    fake_dfs = {
        "Episodes": current_eps,
        "OC3": oc3,
        "Header": header,
        "Episodes_last": prev_eps,
        "metadata": metadata,
    }
    result = validate(fake_dfs)
    assert result == {"OC3": [1, 2, 4, 5, 6, 7]}
