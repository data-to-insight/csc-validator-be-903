from validator903.types import ErrorDefinition


@rule_definition(
    code="103",
    message="The ethnicity code is either not valid or has not been entered.",
    affected_fields=["ETHNIC"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}

    header = dfs["Header"]
    codelist = [
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

    mask = header["ETHNIC"].isin(codelist)

    validationerrormask = ~mask
    validationerrorlocations = header.index[validationerrormask]

    return {"Header": validationerrorlocations.tolist()}


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
