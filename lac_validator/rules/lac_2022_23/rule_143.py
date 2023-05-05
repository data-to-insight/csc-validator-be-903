from validator903.types import ErrorDefinition


@rule_definition(
    code="143",
    message="The reason for new episode code is not a valid code.",
    affected_fields=["RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    codelist = ["S", "P", "L", "T", "U", "B"]

    mask = episodes["RNE"].isin(codelist) | episodes["RNE"].isna()

    validationerrormask = ~mask
    validationerrorlocations = episodes.index[validationerrormask]

    return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "RNE": ["S", "p", "SP", "a", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 3, 4]}
