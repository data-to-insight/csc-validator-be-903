from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="528",
        description="A placement provider code of PR2 cannot be associated with placements P1, R2 or R5.",
        affected_fields=["PLACE", "PLACE_PROVIDER"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            error_mask = (epi["PLACE"].isin(["P1", "R2", "R5"])) & (
                epi["PLACE_PROVIDER"] == "PR2"
            )
            return {"Episodes": epi.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["P1", "A3", "K1", "P1", "P1", "R2"],
            "PLACE_PROVIDER": ["PR2", "PR3", "PR2", "PR4", "PR5", "PR2"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 5]}
