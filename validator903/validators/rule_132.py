from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="132",
        description="Data entry for activity after leaving care is invalid.",
        affected_fields=["ACTIV"],
    )

    def _validate(dfs):
        if "OC3" not in dfs:
            return {}

        care_leavers = dfs["OC3"]
        code_list = [
            "F1",
            "P1",
            "F2",
            "P2",
            "F4",
            "P4",
            "F5",
            "P5",
            "G4",
            "G5",
            "G6",
            "0",
        ]
        mask = care_leavers["ACTIV"].astype(str).isin(code_list)

        validation_error_mask = ~mask
        validation_error_locations = care_leavers.index[validation_error_mask]

        return {"OC3": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "ACTIV": ["f1", "F1", 1, 0, "1", "0", "", pd.NA],
        }
    )

    fake_dfs = {"OC3": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [0, 2, 4, 6, 7]}
