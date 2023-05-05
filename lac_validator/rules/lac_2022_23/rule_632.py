import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="632",
    message="Date of previous permanence order not a valid value. NOTE: This rule may result in false negatives where the period of care started before the current collection year",
    affected_fields=["DATE_PERM", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PrevPerm" not in dfs:
        return {}
    else:
        # function to check that date is of the right format
        def validdate(dte):
            try:
                lst = dte.split("/")
            except AttributeError:
                return pd.NaT
            # Preceding block checks for the scenario where the value passed in is nan/naT

            # date should have three elements
            if len(lst) != 3:
                return pd.NaT

            zlist = ["ZZ", "ZZ", "ZZZZ"]
            # We set the date to the latest possible value to avoid false positives
            offsetlist = [
                pd.DateOffset(months=1, days=-1),
                pd.DateOffset(years=1, days=-1),
                None,
            ]
            # that is, go to the next month/year and take the day before that
            alreadyfoundnonzeds = False
            datebits = []

            for i, zeds, offset in zip(lst, zlist, offsetlist):
                if i == zeds:
                    # I'm assuming it is invalid to have a date like '01/ZZ/ZZZZ'
                    if alreadyfoundnonzeds:
                        return pd.NaT
                    # Replace day & month zeds with '01' so we can check if the resulting date is valid
                    # and set the offset so we can compare the latest corresponding date
                    elif i == "ZZ":
                        i = "01"
                        offsettouse = offset
                else:
                    alreadyfoundnonzeds = True
                datebits.append(i)

            asdatetime = pd.todatetime(
                "/".join(datebits), format="%d/%m/%Y", errors="coerce"
            )
            try:
                asdatetime += offsettouse
            except NameError:  # offsettouse only defined if needed
                pass
            return asdatetime

        episodes = dfs["Episodes"]
        prevperm = dfs["PrevPerm"]

        # convert dates from strings to appropriate format.
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        prevperm["DATEPERMdt"] = prevperm["DATEPERM"].apply(validdate)

        # select first episodes
        firstepsidxs = episodes.groupby("CHILD")["DECOM"].idxmin()
        firsteps = episodes[episodes.index.isin(firstepsidxs)]

        # prepare to merge
        firsteps.resetindex(inplace=True)
        prevperm.resetindex(inplace=True)
        merged = firsteps.merge(
            prevperm, on="CHILD", how="left", suffixes=["eps", "prev"]
        )

        # If provided <DATEPERM> should be prior to <DECOM> and in a valid format and contain a valid date Format should be DD/MM/YYYY or one or more elements of the date can be replaced by ZZ if part of the date element is not known.
        mask = (merged["DATEPERMdt"] >= merged["DECOM"]) | (
            merged["DATEPERM"].notna()
            & merged["DATEPERMdt"].isna()
            & (merged["DATEPERM"] != "ZZ/ZZ/ZZZZ")
        )

        # error locations
        preverrorlocs = merged.loc[mask, "indexprev"]
        epserrorlocs = merged.loc[mask, "indexeps"]

        return {
            "Episodes": epserrorlocs.tolist(),
            "PrevPerm": preverrorlocs.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_prevperm = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "102",
                "103",
                "104",
                "105",
                "106",
                "107",
                "108",
                "109",
                "110",
            ],
            "DATE_PERM": [
                "xx/10/2011",
                "17/06/2001",
                "01/05/2000",
                pd.NA,
                "05/ZZ/2020",
                "ZZ/05/2021",
                "ZZ/ZZ/ZZZZ",
                "ZZ/ZZ/1993",
                "ZZ/ZZ/ZZ",
                "01/13/2000",
            ],
        }
    )

    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "101",
                "DECOM": "20/10/2011",
            },  # 0 - fail! DATE_PERM is not in appropriate format
            {
                "CHILD": "102",
                "DECOM": "19/11/2021",
            },  # 1 pass
            {
                "CHILD": "102",
                "DECOM": "17/06/2001",
            },  # 2 - fail! DATE_PERM == DECOM
            {
                "CHILD": "103",
                "DECOM": pd.NA,
            },  # 3 ignore DECOM is nan
            {
                "CHILD": "104",
                "DECOM": "11/09/2015",
            },  # 4 pass DATE_PERM is nan
            {
                "CHILD": "105",
                "DECOM": "01/03/2021",
            },  # 5 - fail! DATE_PERM wrong format
            {
                "CHILD": "106",
                "DECOM": "01/07/2021",
            },  # 6 pass
            {
                "CHILD": "107",
                "DECOM": "01/07/2021",
            },  # 7 pass
            {
                "CHILD": "108",
                "DECOM": "01/07/2021",
            },  # 8 pass
            {
                "CHILD": "109",
                "DECOM": "01/07/2021",
            },  # 9 - fail! wrong zeds in DATE_PERM
            {
                "CHILD": "110",
                "DECOM": "01/07/2021",
            },  # 10 - fail! wrong month in DATE_PERM
        ]
    )
    fake_dfs = {"PrevPerm": fake_data_prevperm, "Episodes": fake_data_episodes}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    # desired
    assert result == {"Episodes": [0, 2, 5, 9, 10], "PrevPerm": [0, 1, 4, 8, 9]}
