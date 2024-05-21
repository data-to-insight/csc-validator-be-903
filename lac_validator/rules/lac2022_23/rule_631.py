import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="631",
    message="Previous permanence option not a valid value.",
    affected_fields=["PREV_PERM"],
    tables=["PrevPerm"],
)
def validate(dfs):
    if "PrevPerm" not in dfs:
        return {}

    previous_permanence = dfs["PrevPerm"]
    code_list = ["P1", "P2", "P3", "P4", "Z1"]

    mask = (
        previous_permanence["PREV_PERM"].isin(code_list)
        | previous_permanence["PREV_PERM"].isna()
    )

    validation_error_mask = ~mask
    validation_error_locations = previous_permanence.index[validation_error_mask]

    return {"PrevPerm": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PREV_PERM": ["P0", "P1", "p1", "", pd.NA],
        }
    )

    fake_dfs = {"PrevPerm": fake_data}

    result = validate(fake_dfs)

    assert result == {"PrevPerm": [0, 2, 3]}
