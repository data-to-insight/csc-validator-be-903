import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1007",
    message="Care leaver information is not required for 17- or 18-year olds who are still looked after [on "
    "their 17th or 18th birthday.]",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "OC3" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        oc3 = dfs["OC3"]
        collection_end = dfs["metadata"]["collection_end"]
        # convert dates to datetime format
        oc3["DOB"] = pd.to_datetime(oc3["DOB"], format="%d/%m/%Y", errors="coerce")
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC"] = pd.to_datetime(episodes["DEC"], format="%d/%m/%Y")
        episodes["DECOM"] = pd.to_datetime(episodes["DECOM"], format="%d/%m/%Y")

        # prepare to merge
        episodes.reset_index(inplace=True)
        oc3.reset_index(inplace=True)
        merged = episodes.merge(oc3, on="CHILD", how="left", suffixes=["_eps", "_oc3"])
        this_year = collection_end.year

        # If <DOB> < 19 and >= to 17 years prior to <COLLECTION_END_DATE> and current episode <DEC> and or <REC>
        # not provided then <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
        check_age = (
            merged["DOB"] + pd.offsets.DateOffset(years=17) <= collection_end
        ) & (merged["DOB"] + pd.offsets.DateOffset(years=19) > collection_end)
        # That is, check that 17<=age<19

        merged["bday"] = merged["DOB"].apply(lambda x: x.replace(year=this_year))

        merged.loc[merged["bday"] > collection_end, "bday"] -= pd.DateOffset(years=1)

        in_care_on_bday = (merged["DECOM"] <= merged["bday"]) & (
            merged["DEC"] > merged["bday"]
        )

        # if either DEC or REC are absent
        mask = (
            check_age
            & in_care_on_bday
            & merged[["IN_TOUCH", "ACTIV", "ACCOM"]].notna().any(axis=1)
        )
        # Then raise an error if either IN_TOUCH, ACTIV, or ACCOM have been provided too

        # error locations
        oc3_error_locs = merged.loc[mask, "index_oc3"]
        episode_error_locs = merged.loc[mask, "index_eps"]
        # one to many join implies use .unique on the 'one'
        return {"OC3": oc3_error_locs.unique().tolist()}


def test_validate():
    import pandas as pd

    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": ["F", "G", "H", "I"],
            "DOB": ["01/02/2000", "01/09/1999", "01/02/2000", "01/09/1999"],
            "IN_TOUCH": ["notNA", "notNA", "notNA", pd.NA],
            "ACTIV": [pd.NA, pd.NA, pd.NA, pd.NA],
            "ACCOM": [pd.NA, pd.NA, pd.NA, pd.NA],
        }
    )
    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["F", "G", "H", "I"],
            "DECOM": ["01/02/2015", "01/09/2015", "01/02/2015", "01/09/2015"],
            "DEC": ["01/03/2017", "01/09/2016", "01/01/2017", "01/09/2017"],
        }
    )

    metadata = {"collection_end": "31/03/2017"}

    fake_dfs = {
        "Episodes": fake_data_episodes,
        "OC3": fake_data_oc3,
        "metadata": metadata,
    }

    result = validate(fake_dfs)
    assert result == {
        "OC3": [
            0,
        ]
    }
