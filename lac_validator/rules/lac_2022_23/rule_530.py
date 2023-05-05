from validator903.types import ErrorDefinition


@rule_definition(
    code="530",
    message="A placement provider code of PR4 cannot be associated with placement P1.",
    affected_fields=["PLACE", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        mask = episodes["PLACE"].eq("P1") & episodes["PLACEPROVIDER"].eq("PR4")

        validationerrormask = mask
        validationerrorlocations = episodes.index[validationerrormask]

        return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["P1", "A3", "K1", "P1", "P1", "P1"],
            "PLACE_PROVIDER": ["PR4", "PR3", "PR4", "PR4", "PR5", "PRO"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 3]}
