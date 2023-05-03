from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="408",
        description="Child is placed for adoption with a placement order, but no placement order has been recorded.",
        affected_fields=["PLACE", "LS"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            error_mask = epi["PLACE"].isin(["A5", "A6"]) & (epi["LS"] != "E1")
            return {"Episodes": epi.index[error_mask].to_list()}

    return error, _validate


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
