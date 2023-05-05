import pandas as pd

from validator903.types import ErrorDefinition


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
        collectionend = dfs["metadata"]["collectionend"]
        # convert dates to datetime format
        oc3["DOB"] = pd.todatetime(oc3["DOB"], format="%d/%m/%Y", errors="coerce")
        collectionend = pd.todatetime(collectionend, format="%d/%m/%Y", errors="coerce")
        episodes["DEC"] = pd.todatetime(episodes["DEC"], format="%d/%m/%Y")
        episodes["DECOM"] = pd.todatetime(episodes["DECOM"], format="%d/%m/%Y")

        # prepare to merge
        episodes.resetindex(inplace=True)
        oc3.resetindex(inplace=True)
        merged = episodes.merge(oc3, on="CHILD", how="left", suffixes=["eps", "oc3"])
        thisyear = collectionend.year

        # If <DOB> < 19 and >= to 17 years prior to <COLLECTIONENDDATE> and current episode <DEC> and or <REC>
        # not provided then <INTOUCH>, <ACTIV> and <ACCOM> should not be provided
        checkage = (
            merged["DOB"] + pd.offsets.DateOffset(years=17) <= collectionend
        ) & (merged["DOB"] + pd.offsets.DateOffset(years=19) > collectionend)
        # That is, check that 17<=age<19

        merged["bday"] = merged["DOB"].apply(lambda x: x.replace(year=thisyear))

        merged.loc[merged["bday"] > collectionend, "bday"] -= pd.DateOffset(years=1)

        incareonbday = (merged["DECOM"] <= merged["bday"]) & (
            merged["DEC"] > merged["bday"]
        )
        print(incareonbday)
        # if either DEC or REC are absent
        mask = (
            checkage
            & incareonbday
            & merged[["INTOUCH", "ACTIV", "ACCOM"]].notna().any(axis=1)
        )
        # Then raise an error if either INTOUCH, ACTIV, or ACCOM have been provided too

        # error locations
        oc3errorlocs = merged.loc[mask, "indexoc3"]
        episodeerrorlocs = merged.loc[mask, "indexeps"]
        # one to many join implies use .unique on the 'one'
        return {"OC3": oc3errorlocs.unique().tolist()}


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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {
        "OC3": [
            0,
        ]
    }
