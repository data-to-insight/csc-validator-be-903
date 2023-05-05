from validator903.types import ErrorDefinition


@rule_definition(
    code="380",
    message="A period of care cannot start with a temporary placement.",
    affected_fields=["PLACE", "RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        errormask = (epi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4"])) & (
            ~epi["RNE"].isin(["P", "B"])
        )
        return {"Episodes": epi.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "RNE": ["S", "L", "P", "B", "P", pd.NA],
            "PLACE": ["U1", "T0", "U2", "Z1", "T1", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1]}
