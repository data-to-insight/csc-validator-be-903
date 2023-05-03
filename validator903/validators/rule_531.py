from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="531",
        description="A placement provider code of PR5 cannot be associated with placements P1.",
        affected_fields=["PLACE", "PLACE_PROVIDER"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            error_mask = (epi["PLACE"] == "P1") & (epi["PLACE_PROVIDER"] == "PR5")
            return {"Episodes": epi.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["P1", "A3", "K1", "P1", "P1", "P1"],
            "PLACE_PROVIDER": ["PR5", "PR3", "PR4", "PR4", "PR5", "PRO"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 4]}
