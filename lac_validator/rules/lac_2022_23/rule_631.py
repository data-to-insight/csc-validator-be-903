from validator903.types import ErrorDefinition


@rule_definition(
    code="631",
    message="Previous permanence option not a valid value.",
    affected_fields=["PREV_PERM"],
)
def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}

    previouspermanence = dfs["PrevPerm"]
    codelist = ["P1", "P2", "P3", "P4", "Z1"]

    mask = (
        previouspermanence["PREVPERM"].isin(codelist)
        | previouspermanence["PREVPERM"].isna()
    )

    validationerrormask = ~mask
    validationerrorlocations = previouspermanence.index[validationerrormask]

    return {"PrevPerm": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PREV_PERM": ["P0", "P1", "p1", "", pd.NA],
        }
    )

    fake_dfs = {"PrevPerm": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"PrevPerm": [0, 2, 3]}
