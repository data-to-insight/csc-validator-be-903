import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="358",
        description="Child with this legal status should not be under 10.",
        affected_fields=["DECOM", "DOB", "LS"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "Header" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            header = dfs["Header"]
            code_list = ["J1", "J2", "J3"]

            # convert dates to datetime format
            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            header["DOB"] = pd.to_datetime(
                header["DOB"], format="%d/%m/%Y", errors="coerce"
            )
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            merged = episodes.merge(
                header, on="CHILD", how="left", suffixes=["_eps", "_er"]
            )

            # Where <LS> = ‘J1’ or ‘J2’ or ‘J3’ then <DOB> should <= to 10 years prior to <DECOM>
            mask = merged["LS"].isin(code_list) & (
                merged["DOB"] + pd.offsets.DateOffset(years=10) >= merged["DECOM"]
            )
            # That is, raise error if DECOM <= DOB + 10years

            # error locations
            header_error_locs = merged.loc[mask, "index_er"]
            episode_error_locs = merged.loc[mask, "index_eps"]
            # one to many join implies use .unique on the 'one'
            return {
                "Episodes": episode_error_locs.tolist(),
                "Header": header_error_locs.unique().tolist(),
            }

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {"CHILD": 101, "DECOM": "01/01/2009", "LS": "J3"},  # 0 Fail
            {"CHILD": 102, "DECOM": "01/01/2001", "LS": "X"},  # 1
            {"CHILD": 103, "DECOM": "20/12/2001", "LS": "L2"},  # 2
            {"CHILD": 104, "DECOM": "03/01/2018", "LS": "J2"},  # 3 Pass
            {"CHILD": 105, "DECOM": "03/04/2008", "LS": "J1"},  # 4 Fail
            {"CHILD": 106, "DECOM": "01/01/2002", "LS": "L2"},  # 5
            {"CHILD": 107, "DECOM": "10/01/2002", "LS": "X"},  # 6
            {"CHILD": 108, "DECOM": "11/02/2012", "LS": "J1"},  # 7 Pass
            {"CHILD": 109, "DECOM": "25/01/2002", "LS": "L2"},  # 8
            {"CHILD": 110, "DECOM": "25/01/2002", "LS": "L2"},  # 9
            {"CHILD": 111, "DECOM": pd.NA, "LS": "J2"},  # 10 ignored by dropna
            {"CHILD": 112, "DECOM": "25/01/2002", "LS": "J3"},  # 11 ignored by dropna
        ]
    )
    fake_data_header = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DOB": "01/01/2000",
            },  # 0
            {
                "CHILD": 102,
                "DOB": "01/01/2001",
            },  # 1
            {
                "CHILD": 103,
                "DOB": "20/12/2001",
            },  # 2
            {
                "CHILD": 104,
                "DOB": "01/01/2000",
            },  # 3
            {
                "CHILD": 105,
                "DOB": "03/01/2000",
            },  # 4
            {
                "CHILD": 106,
                "DOB": "01/01/2002",
            },  # 5
            {
                "CHILD": 107,
                "DOB": "10/01/2002",
            },  # 6
            {
                "CHILD": 108,
                "DOB": "11/01/2002",
            },  # 7
            {
                "CHILD": 109,
                "DOB": "25/01/2002",
            },  # 8
            {
                "CHILD": 110,
                "DOB": "25/01/2002",
            },  # 9
            {
                "CHILD": 111,
                "DOB": "25/01/2002",
            },  # 10
            {
                "CHILD": 112,
                "DOB": pd.NA,
            },  # 11
        ]
    )
    fake_dfs = {"Episodes": fake_data_eps, "Header": fake_data_header}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 4], "Header": [0, 4]}
