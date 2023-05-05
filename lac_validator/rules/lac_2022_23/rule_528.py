from validator903.types import ErrorDefinition


@rule_definition(
    code="528",
    message="A placement provider code of PR2 cannot be associated with placements P1, R2 or R5.",
    affected_fields=["PLACE", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        errormask = (epi["PLACE"].isin(["P1", "R2", "R5"])) & (
            epi["PLACEPROVIDER"] == "PR2"
        )
        return {"Episodes": epi.index[errormask].tolist()}


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
