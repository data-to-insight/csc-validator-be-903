import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


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
        def valid_date(dte):
            try:
                lst = dte.split("/")
            except AttributeError:
                return pd.NaT
            # Preceding block checks for the scenario where the value passed in is nan/naT

            # date should have three elements
            if len(lst) != 3:
                return pd.NaT

            z_list = ["ZZ", "ZZ", "ZZZZ"]
            # We set the date to the latest possible value to avoid false positives
            offset_list = [
                pd.DateOffset(months=1, days=-1),
                pd.DateOffset(years=1, days=-1),
                None,
            ]
            # that is, go to the next month/year and take the day before that
            already_found_non_zeds = False
            date_bits = []

            for i, zeds, offset in zip(lst, z_list, offset_list):
                if i == zeds:
                    # I'm assuming it is invalid to have a date like '01/ZZ/ZZZZ'
                    if already_found_non_zeds:
                        return pd.NaT
                    # Replace day & month zeds with '01' so we can check if the resulting date is valid
                    # and set the offset so we can compare the latest corresponding date
                    elif i == "ZZ":
                        i = "01"
                        offset_to_use = offset
                else:
                    already_found_non_zeds = True
                date_bits.append(i)

            as_datetime = pd.to_datetime(
                "/".join(date_bits), format="%d/%m/%Y", errors="coerce"
            )
            try:
                as_datetime += offset_to_use
            except NameError:  # offset_to_use only defined if needed
                pass
            return as_datetime

        episodes = dfs["Episodes"]
        prevperm = dfs["PrevPerm"]

        # convert dates from strings to appropriate format.
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        prevperm["DATE_PERM_dt"] = prevperm["DATE_PERM"].apply(valid_date)

        # select first episodes
        first_eps_idxs = episodes.groupby("CHILD")["DECOM"].idxmin()
        first_eps = episodes[episodes.index.isin(first_eps_idxs)]

        # prepare to merge
        first_eps.reset_index(inplace=True)
        prevperm.reset_index(inplace=True)
        merged = first_eps.merge(
            prevperm, on="CHILD", how="left", suffixes=["_eps", "_prev"]
        )

        # If provided <DATE_PERM> should be prior to <DECOM> and in a valid format and contain a valid date Format should be DD/MM/YYYY or one or more elements of the date can be replaced by ZZ if part of the date element is not known.
        mask = (merged["DATE_PERM_dt"] >= merged["DECOM"]) | (
            merged["DATE_PERM"].notna()
            & merged["DATE_PERM_dt"].isna()
            & (merged["DATE_PERM"] != "ZZ/ZZ/ZZZZ")
        )

        # error locations
        prev_error_locs = merged.loc[mask, "index_prev"]
        eps_error_locs = merged.loc[mask, "index_eps"]

        return {
            "Episodes": eps_error_locs.tolist(),
            "PrevPerm": prev_error_locs.unique().tolist(),
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
