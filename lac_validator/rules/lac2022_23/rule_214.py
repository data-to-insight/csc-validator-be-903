import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="214",
    message="Placement location information not required.",
    affected_fields=["PL_POST", "URN"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        mask = df["LS"].isin(["V3", "V4"]) & (
            (df["PL_POST"].notna()) | (df["URN"].notna())
        )
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"LS": "V3", "PL_POST": "M2 3RT", "URN": "XXXXXX"},  # 0  Fail
            {"LS": "U1", "PL_POST": "M2 3RT", "URN": "SC045099"},  # 1
            {"LS": "U3", "PL_POST": pd.NA, "URN": "SC045099"},  # 2
            {"LS": "V4", "PL_POST": "M2 3RT", "URN": pd.NA},  # 3  Fail
            {"LS": "V4", "PL_POST": pd.NA, "URN": "SC045099"},  # 4  Fail
            {"LS": "T1", "PL_POST": "M2 3RT", "URN": "SC045100"},  # 5
            {"LS": "U6", "PL_POST": "M2 3RT", "URN": "SC045101"},  # 6
            {"LS": "V3", "PL_POST": pd.NA, "URN": pd.NA},  # 7
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 3, 4]}
