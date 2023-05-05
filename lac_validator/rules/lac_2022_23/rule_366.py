from validator903.types import ErrorDefinition


@rule_definition(
    code="366",
    message="A child cannot change placement during the course of an individual short-term respite break.",
    affected_fields=["RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        mask = (df["LS"] == "V3") & (df["RNE"] != "S")
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"LS": "V3", "RNE": "S"},  # 0
            {"LS": "V4", "RNE": "T"},  # 1
            {"LS": "U1", "RNE": pd.NA},  # 2
            {"LS": "U2", "RNE": pd.NA},  # 3
            {"LS": "V3", "RNE": "U"},  # 4  Fail
            {"LS": "V3", "RNE": pd.NA},  # 5  Fail
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [4, 5]}
