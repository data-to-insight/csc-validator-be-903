import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="407",
    message="Reason episode ceased is Special Guardianship Order, but child has reached age 18.",
    affected_fields=["DEC", "DOB", "REC"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        header = dfs["Header"]
        code_list = ["E45", "E46", "E47", "E48"]

        # convert dates to datetime format
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
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

        # If <REC> = ‘E45’ or ‘E46’ or ‘E47’ or ‘E48’ then <DOB> must be < 18 years prior to <DEC>
        mask = merged["REC"].isin(code_list) & (
            merged["DOB"] + pd.offsets.DateOffset(years=18) < merged["DEC"]
        )
        # That is, raise error if DEC > DOB + 10years

        # error locations
        header_error_locs = merged.loc[mask, "index_er"]
        episode_error_locs = merged.loc[mask, "index_eps"]
        # one to many join implies use .unique on the 'one'
        return {
            "Episodes": episode_error_locs.tolist(),
            "Header": header_error_locs.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {"CHILD": 101, "DEC": "01/01/2009", "REC": "E45"},  # 0 pass
            {"CHILD": 102, "DEC": "01/01/2001", "REC": "A3"},  # 1
            {"CHILD": 103, "DEC": "20/12/2001", "REC": "E15"},  # 2
            {"CHILD": 104, "DEC": "03/01/2019", "REC": "E46"},  # 3 fail
            {"CHILD": 105, "DEC": "03/04/2008", "REC": "E48"},  # 4 pass
            {"CHILD": 106, "DEC": "01/01/2002", "REC": "X2"},  # 5
            {"CHILD": 107, "DEC": "10/01/2002", "REC": "E11"},  # 6
            {"CHILD": 108, "DEC": "11/02/2020", "REC": "E48"},  # 7 fail
            {"CHILD": 109, "DEC": "25/01/2002", "REC": "X1"},  # 8
            {"CHILD": 110, "DEC": "25/01/2002", "REC": "E47"},  # 9
            {"CHILD": 111, "DEC": pd.NA, "REC": "E45"},  # 10 ignored by dropna
            {"CHILD": 112, "DEC": "25/01/2002", "REC": "E46"},  # 11 ignored by dropna
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
    assert result == {"Episodes": [3, 7], "Header": [3, 7]}
