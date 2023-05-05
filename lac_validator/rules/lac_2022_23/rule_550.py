from validator903.types import ErrorDefinition


@rule_definition(
    code="550",
    message="A placement provider code of PR0 can only be associated with placement P1.",
    affected_fields=["PLACE", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]

        mask = (episodes["PLACE"] != "P1") & episodes["PLACEPROVIDER"].eq("PR0")

        validationerrorlocations = episodes.index[mask]
        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["P1", "P0", "T1", "T3", "T1", "P1", "P0"],
            "PLACE_PROVIDER": ["PR0", "PR2", "PR4", "PR0", pd.NA, "PR0", "PR0"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 6]}
