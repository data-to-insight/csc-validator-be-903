import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="148",
    message="Date episode ceased and reason episode ceased must both be coded, or both left blank.",
    affected_fields=["DEC", "REC"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]

        mask = ((df["DEC"].isna()) & (df["REC"].notna())) | (
            (df["DEC"].notna()) & (df["REC"].isna())
        )

        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
                "REC": pd.NA,
            },  # 0  Fails
            {
                "CHILD": "111",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
                "REC": "X1",
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "06/06/2020",
                "DEC": pd.NA,
                "REC": "X1",
            },  # 2   Fails
            {
                "CHILD": "111",
                "DECOM": "08/06/2020",
                "DEC": "05/06/2020",
                "REC": "X1",
            },  # 3
            {
                "CHILD": "222",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
                "REC": pd.NA,
            },  # 4   Fails
            {
                "CHILD": "333",
                "DECOM": "06/06/2020",
                "DEC": "07/06/2020",
                "REC": "E11",
            },  # 5
            {"CHILD": "333", "DECOM": "07/06/2020", "DEC": pd.NA, "REC": pd.NA},  # 6
            {
                "CHILD": "444",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
                "REC": "X1",
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "09/06/2020",
                "DEC": "10/06/2020",
                "REC": "E11",
            },  # 8
            {"CHILD": "444", "DECOM": "15/06/2020", "DEC": pd.NA, "REC": pd.NA},  # 9
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 2, 4]}
