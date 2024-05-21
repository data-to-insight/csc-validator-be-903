import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="526",
    message="Child is missing a placement provider code for at least one episode.",
    affected_fields=["PLACE", "PLACE_PROVIDER"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        error_mask = (
            ~epi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4", "Z1"])
            & epi["PLACE_PROVIDER"].isna()
        )
        return {"Episodes": epi.index[error_mask].to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["E1", "P0", "T1", "T3", "P1", "Z1", "P0"],
            "PLACE_PROVIDER": ["PR1", "PR2", pd.NA, "PR0", pd.NA, pd.NA, pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    assert validate(fake_dfs) == {"Episodes": [4, 6]}
