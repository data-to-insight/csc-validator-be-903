from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="411",
        description="Placement location code disagrees with LA of placement.",
        affected_fields=["PL_LOCATION"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            df = dfs["Episodes"]
            local_authority = dfs["metadata"]["localAuthority"]

            mask = df["PL_LOCATION"].eq("IN") & df["PL_LA"].ne(local_authority)

            return {"Episodes": df.index[mask].tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PL_LA": ["auth", "somewhere else", "auth", "auth", "somewhere else"],
            "PL_LOCATION": ["IN", "OUT", pd.NA, "OUT", "IN"],
        }
    )

    fake_dfs = {"Episodes": fake_data, "metadata": {"localAuthority": "auth"}}

    error_defn, error_func = validate()

    # Note 2 and 3 pass as the rule is specific
    # about only checking that 'IN' is set correctly
    assert error_func(fake_dfs) == {"Episodes": [4]}
