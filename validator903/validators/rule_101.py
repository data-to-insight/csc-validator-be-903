from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="101",
        description="Gender code is not valid.",
        affected_fields=["SEX"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}

        header = dfs["Header"]
        code_list = ["1", "2"]

        mask = header["SEX"].astype(str).isin(code_list)

        validation_error_mask = ~mask
        validation_error_locations = header.index[validation_error_mask]

        return {"Header": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": [1, 2, 3, pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [2, 3]}
