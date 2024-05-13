import pandas as pd
import numpy as np

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
        df = dfs["Header"]

        valid_ethnic_codes = [
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

        condition =  ~(df["ETHNIC"].isin(valid_ethnic_codes))

        error_rows = df[condition].index

        return {"Header": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_header = pd.DataFrame(
        {
            "ETHNIC": ["WBRI", # 0 pass
                       "WIRI", # 1 pass
                       "WOTH", # 2 pass
                       "wbri", # 3 fail, lower case
                       "White British", #  4 fail, not in ethnicity list
                       "", # 5 fail empty string
                       pd.NA], # 6 fail NA

        }
    )

    fake_dfs = ["Header": fake_header]

    result = validate(fake_dfs)

    assert result == {"Header": [3, 4, 5, 6]}
