import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="702",
    message="The date that the DoLO ended is before the date that it started.",
    affected_fields=["DOLO_START"],
    tables=["DoLo"],
)
def validate(dfs):
    if "DoLo" not in dfs:
        return {}

    dolo = dfs["DoLo"]

    dolo["DOLO_START_dt"] = pd.to_datetime(
        dolo["DOLO_START"], format="%d/%m/%Y", errors="coerce"
    )

    dolo["DOLO_END_dt"] = pd.to_datetime(
        dolo["DOLO_END"], format="%d/%m/%Y", errors="coerce"
    )

    error_rows = dolo.index[
        (dolo["DOLO_END_dt"] <= dolo["DOLO_START_dt"])
        & (dolo["DOLO_END_dt"].notna())
        & (dolo["DOLO_START_dt"].notna())
    ]

    return {"DoLo": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOLO_START": [
                "01/01/2000",
                "01/01/2000",
                pd.NA,
                "02/01/2000",
                "01/01/2000",
            ],
            "DOLO_END": ["01/01/2000", pd.NA, "2000/12/10", "01/01/2000", "02/10/2000"],
        }
    )

    fake_dfs = {"DoLo": fake_data}

    result = validate(fake_dfs)

    assert result == {"DoLo": [0, 3]}
