import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="521",
    message="Date of local authority's decision (LA) that adoption is in the best interests of the child (date should be placed) must be on or prior to the date the child is placed for adoption.",
    affected_fields=["PLACE", "DECOM", "DATE_INT"],
)
def validate(dfs):
    if "Episodes" not in dfs or "AD1" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        ad1 = dfs["AD1"]
        codelist = ["A3", "A4", "A5", "A6"]
        # if PLACE is equal to A3, A4, A5 or A6 then placed-for-adoption = Y

        # to datetime
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        ad1["DATEINT"] = pd.todatetime(
            ad1["DATEINT"], format="%d/%m/%Y", errors="coerce"
        )

        # prepare to merge
        episodes.resetindex(inplace=True)
        ad1.resetindex(inplace=True)
        merged = episodes.merge(ad1, how="left", on="CHILD", suffixes=["eps", "ad1"])

        # <DATEINT> must be <= <DECOM> where <PLACEDFORADOPTION> = 'Y'
        mask = merged["PLACE"].isin(codelist) & (merged["DATEINT"] > merged["DECOM"])
        # error locations
        ad1errorlocs = merged.loc[mask, "indexad1"]
        epserrorlocs = merged.loc[mask, "indexeps"]
        return {"Episodes": epserrorlocs.tolist(), "AD1": ad1errorlocs.tolist()}


def test_validate():
    import pandas as pd

    fake_ad1 = pd.DataFrame(
        {
            "DATE_INT": [
                "08/03/2020",
                "22/07/2020",
                "13/10/2021",
                "22/06/2020",
                pd.NA,
            ],
            "CHILD": [
                "111",
                "123",
                "333",
                "444",
                "678",
            ],
        }
    )
    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/01/2020",
                "PLACE": "A6",
            },  # 0 fail
            {
                "CHILD": "111",
                "DECOM": "01/11/2020",
                "PLACE": "A5",
            },  # 1 pass
            {
                "CHILD": "111",
                "DECOM": "22/01/2020",
                "PLACE": "X1",
            },  # 2 ignore PLACE not in list
            {
                "CHILD": "123",
                "DECOM": pd.NA,
                "PLACE": "A5",
            },  # 3 ignore DECOM is nan
            {
                "CHILD": "123",
                "DECOM": "11/01/2020",
                "PLACE": "X1",
            },  # 4 ignore PLACE not in list
            {
                "CHILD": "333",
                "DECOM": "01/01/2020",
                "PLACE": "A6",
            },  # 5 fail
            {
                "CHILD": "333",
                "DECOM": "22/01/2020",
                "PLACE": "X1",
            },  # 6 ignore PLACE not in list
            {
                "CHILD": "333",
                "DECOM": "11/01/2020",
                "PLACE": "U1",
            },  # 7 ignore PLACE not in list
            {
                "CHILD": "444",
                "DECOM": "22/06/2020",
                "PLACE": "A3",
            },  # 8 pass
            {
                "CHILD": "444",
                "DECOM": "11/01/2020",
                "PLACE": "X1",
            },  # 9 ignore PLACE not in list
            {
                "CHILD": "444",
                "DECOM": "01/01/2020",
                "PLACE": "A3",
            },  # 10 fail
            {
                "CHILD": "678",
                "DECOM": "01/01/2020",
                "PLACE": "A4",
            },  # 11 ignore DATE_INT is nan
        ]
    )
    fake_dfs = {"Episodes": fake_data_episodes, "AD1": fake_ad1}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 5, 10], "AD1": [0, 2, 3]}
