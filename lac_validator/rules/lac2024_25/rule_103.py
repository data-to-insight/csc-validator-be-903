import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="103",
    message="The ethnicity code is either not valid or has not been entered.",
    affected_fields=["ETHNIC"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        ethn_code_list = [
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

    condition = ~(df["ETHNIC"].isin(ethn_code_list))
    error_rows = df[condition].index

    return {"Header": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_header = pd.DataFrame(
        {
            "ETHNIC": [
                "WBRI",  # 0 pass
                "WIRI",  # 1 pass
                "WOTH",  # 2 pass
                "wbri",
                "White British",
                "",
                pd.NA,  # 3, 4,5,6 fail
            ],
        }
    )

    fake_dfs = {"Header": fake_header}

    result = validate(fake_dfs)

    assert result == {"Header": [3, 4, 5, 6]}
