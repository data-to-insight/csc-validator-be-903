from validator903.types import ErrorDefinition


@rule_definition(
    code="381",
    message="A period of care cannot end with a temporary placement.",
    affected_fields=["PLACE", "REC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        errormask = (
            (epi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4"]))
            & (epi["REC"] != "X1")
            & (epi["REC"].notna())
        )
        return {"Episodes": epi.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REC": ["X1", "PR1", "X1", pd.NA, "X1", pd.NA],
            "PLACE": ["T3", "T0", "U2", "T2", "T1", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1]}
