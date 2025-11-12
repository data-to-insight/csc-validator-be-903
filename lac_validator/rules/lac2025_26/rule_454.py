import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="454",
    message="Placement distance from home is over 350 miles. [NOTE: This check will result in false positives for children formerly UASC not identified as such in loaded data]",
    affected_fields=["PL_DISTANCE"],
    tables=["Episodes"],
)
def validate(dfs):
    # If <PL_DISTANCE> is present and not 999.9, then <PL_DISTANCE> should be <=350 miles
    if "Episodes" not in dfs:
        return {}

    df = dfs["Episodes"]

    df.reset_index(inplace=True)

    has_pl_distance = df["PL_DISTANCE"].notna()

    over_350_not_999 = (df["PL_DISTANCE"] > 350) & (df["PL_DISTANCE"] != 999.9)

    failure_rows = df[has_pl_distance & over_350_not_999]["index"].to_list()

    return {"Episodes": failure_rows}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PL_DISTANCE": [350, 999.9, 349, -351, 999, 998, 351, pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [4, 5, 6]}
