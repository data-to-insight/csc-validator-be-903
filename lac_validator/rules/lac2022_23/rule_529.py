import pandas as pd

from lac_validator.rule_engine import rule_definition


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
        code_list_placement_type = [
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
        error_mask = epi["PLACE"].isin(code_list_placement_type) & (
            epi["PLACE_PROVIDER"] == "PR3"
        )
        return {"Episodes": epi.index[error_mask].to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE_PROVIDER": ["PR0", "PR1", "PR3", "PR3", pd.NA, "PR3"],
            "PLACE": ["U1", "U2", "U3", "T1", pd.NA, "A3"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [2, 5]}
