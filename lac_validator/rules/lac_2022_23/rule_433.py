import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="433",
    message="The reason for new episode suggests that this is a continuation episode, but the episode does not start on the same day as the last episode finished.",
    affected_fields=["RNE", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOMdt"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECdt"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        episodes["originalindex"] = episodes.index
        episodes.sortvalues(["CHILD", "DECOMdt", "DECdt"], inplace=True)
        episodes[["PREVIOUSDEC", "PREVIOUSCHILD"]] = episodes[["DEC", "CHILD"]].shift(1)

        rneisongoing = (
            episodes["RNE"].str.upper().astype(str).isin(["P", "L", "T", "U", "B"])
        )
        datemismatch = episodes["PREVIOUSDEC"] != episodes["DECOM"]
        missingdate = episodes["PREVIOUSDEC"].isna() | episodes["DECOM"].isna()
        samechild = episodes["PREVIOUSCHILD"] == episodes["CHILD"]

        errormask = rneisongoing & (datemismatch | missingdate) & samechild

        errorlocations = episodes["originalindex"].loc[errormask].sortvalues()

        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "101",
                "DECOM": "20/10/2021",
                "RNE": "S",
                "DEC": "20/11/2021",
            },  # 0: Ignore
            {
                "CHILD": "102",
                "DECOM": "19/11/2021",
                "RNE": "P",
                "DEC": pd.NA,
            },  # 1 [102:2nd]
            {
                "CHILD": "102",
                "DECOM": "17/06/2021",
                "RNE": "P",
                "DEC": "19/11/2021",
            },  # 2 [102:1st]
            {
                "CHILD": "103",
                "DECOM": "04/04/2020",
                "RNE": "B",
                "DEC": "12/09/2020",
            },  # 3 [103:1st]
            {
                "CHILD": "103",
                "DECOM": "11/09/2020",
                "RNE": "B",
                "DEC": "06/05/2021",
            },  # 4 [103:2nd] ]Fail!
            {
                "CHILD": "103",
                "DECOM": "07/05/2021",
                "RNE": "B",
                "DEC": pd.NA,
            },  # 5 [103:3rd] Fail!
        ]
    )

    fake_dfs = {"Episodes": fake_data_episodes}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [4, 5]}
