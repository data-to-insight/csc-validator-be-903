from validator903.types import ErrorDefinition


@rule_definition(
    code="529",
    message="Placement provider code of PR3 cannot be associated with placements P1, A3 to A6, K1, K2 and U1 to U6 as these placements cannot be provided by other public organisations.",
    affected_fields=["PLACE", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        codelistplacementtype = [
            "A3",
            "A4",
            "A5",
            "A6",
            "K1",
            "K2",
            "P1",
            "U1",
            "U2",
            "U3",
            "U4",
            "U5",
            "U6",
        ]
        errormask = epi["PLACE"].isin(codelistplacementtype) & (
            epi["PLACEPROVIDER"] == "PR3"
        )
        return {"Episodes": epi.index[errormask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE_PROVIDER": ["PR0", "PR1", "PR3", "PR3", pd.NA, "PR3"],
            "PLACE": ["U1", "U2", "U3", "T1", pd.NA, "A3"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 5]}
