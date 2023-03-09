from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="103",
        description="The ethnicity code is either not valid or has not been entered.",
        affected_fields=["ETHNIC"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}

        header = dfs["Header"]
        code_list = [
            "WBRI",
            "WIRI",
            "WOTH",
            "WIRT",
            "WROM",
            "MWBC",
            "MWBA",
            "MWAS",
            "MOTH",
            "AIND",
            "APKN",
            "ABAN",
            "AOTH",
            "BCRB",
            "BAFR",
            "BOTH",
            "CHNE",
            "OOTH",
            "REFU",
            "NOBT",
        ]

        mask = header["ETHNIC"].isin(code_list)

        validation_error_mask = ~mask
        validation_error_locations = header.index[validation_error_mask]

        return {"Header": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "ETHNIC": ["WBRI", "WIRI", "WOTH", "wbri", "White British", "", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [3, 4, 5, 6]}
