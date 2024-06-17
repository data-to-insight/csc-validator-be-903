import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="527",
    message="A placement provider code of PR1 cannot be associated with placements P1, R2 or R5.",
    affected_fields=["PLACE", "PLACE_PROVIDER"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        error_mask = (epi["PLACE"].isin(["P1", "R2", "R5"])) & (
            epi["PLACE_PROVIDER"] == "PR1"
        )
        return {"Episodes": epi.index[error_mask].to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["P1", "A3", "K1", "R2", "P1", "X1"],
            "PLACE_PROVIDER": ["PR1", "PR3", "PR4", "PR1", "PR1", "PR1"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 3, 4]}
