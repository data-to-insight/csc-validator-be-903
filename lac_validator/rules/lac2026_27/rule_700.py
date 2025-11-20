import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="700",
    message="The start date of the DoLO is not a valid date.",
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

    error_rows = dolo.index[dolo["DOLO_START_dt"].isna()]

    return {"DoLo": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOLO_START": [
                "01/01/2020",
                pd.NA,
                "2000/12/10",
            ],
        }
    )

    fake_dfs = {"DoLo": fake_data}

    result = validate(fake_dfs)

    assert result == {"DoLo": [1, 2]}
