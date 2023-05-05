from validator903.types import ErrorDefinition


@rule_definition(
    code="408",
    message="Child is placed for adoption with a placement order, but no placement order has been recorded.",
    affected_fields=["PLACE", "LS"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        errormask = epi["PLACE"].isin(["A5", "A6"]) & (epi["LS"] != "E1")
        return {"Episodes": epi.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"PLACE": "A5", "LS": "S"},  # 0   Fail
            {"PLACE": "V4", "LS": "T"},  # 1
            {"PLACE": "A6", "LS": "E1"},  # 2
            {"PLACE": "U2", "LS": pd.NA},  # 3
            {"PLACE": "A6", "LS": "U"},  # 4  Fail
            {"PLACE": "A5", "LS": pd.NA},  # 5  Fail
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 4, 5]}
