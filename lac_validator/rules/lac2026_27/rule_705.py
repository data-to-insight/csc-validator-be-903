import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="705",
    message="A DoLO cannot start when the previous DoLO is still open.",
    affected_fields=["DOLO_START", "DOLO_END"],
    tables=["DoLo"],
)
def validate(dfs):
    # If provided <DOLO_START> from current
    # DoLO occurrence must be >= previous DoLO occurrence <DOLO_START>
    # and previous DoLO occurrence <DOLO_END> cannot be Null

    if "DoLo" not in dfs:
        return {}

    dolo = dfs["DoLo"]
    dolo["DOLO_START"] = pd.to_datetime(
        dolo["DOLO_START"], format="%d/%m/%Y", errors="coerce"
    )
    dolo["DOLO_END"] = pd.to_datetime(
        dolo["DOLO_END"], format="%d/%m/%Y", errors="coerce"
    )

    dolo["DOLO_END_FILL"] = dolo["DOLO_END"].fillna(dolo["DOLO_START"])
    dolo.sort_values(["CHILD", "DOLO_END_FILL", "DOLO_START"], inplace=True)

    dolo.reset_index(inplace=True)
    dolo.reset_index(inplace=True)  # Twice on purpose

    dolo["LAG_INDEX"] = dolo["level_0"].shift(-1)

    lag_dolo = dolo.merge(
        dolo,
        how="inner",
        left_on="level_0",
        right_on="LAG_INDEX",
        suffixes=["", "_PREV"],
    )

    # We're only interested in cases where there is more than one row for a child.
    lag_dolo = lag_dolo[lag_dolo["CHILD"] == lag_dolo["CHILD_PREV"]]

    # A previous dolo_END date is null
    mask1 = lag_dolo["DOLO_END_PREV"].isna()
    # dolo_START is before previous dolo_END (overlapping dates)
    mask2 = lag_dolo["DOLO_START"] < lag_dolo["DOLO_END_PREV"]

    mask = mask1 | mask2

    error_list = lag_dolo["index"][mask].to_list()
    error_list.sort()
    return {"DoLo": error_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": [1, 1, 1, 2, 2, 3, 4, 4, 4],
            "DOLO_START": [
                "01/01/2000",
                "04/01/2000",
                "03/01/2000",
                "01/01/2000",
                "02/01/2000",
                "01/01/2000",
                "01/04/2025",
                "04/04/2025",
                "08/04/2025",
            ],
            "DOLO_END": [
                "02/01/2000",
                "04/01/2000",
                "06/01/2000",
                pd.NA,
                "02/01/2000",
                "02/01/2000",
                "o2/04/2025",
                pd.NA,
                "10/04/2025",
            ],
        }
    )

    fake_dfs = {"DoLo": fake_data}

    result = validate(fake_dfs)

    assert result == {"DoLo": [2, 4, 7, 8]}
