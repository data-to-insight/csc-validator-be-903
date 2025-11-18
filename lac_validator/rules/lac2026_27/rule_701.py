import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="701",
    message="The end date of the DoLO is not a valid date.",
    affected_fields=["DOLO_START"],
    tables=["DoLo"],
)
def validate(dfs):
    if "DoLo" not in dfs:
        return {}

    dolo = dfs["DoLo"]

    no_empty_ends = dolo[dolo["DOLO_END"].notna()].copy()

    no_empty_ends["DOLO_END_dt"] = pd.to_datetime(
        no_empty_ends["DOLO_END"], format="%d/%m/%Y", errors="coerce"
    )

    error_rows = no_empty_ends.index[no_empty_ends["DOLO_END_dt"].isna()]

    return {"DoLo": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOLO_END": [
                "01/01/2020",
                pd.NA,
                "2000/12/10",
            ],
        }
    )

    fake_dfs = {"DoLo": fake_data}

    result = validate(fake_dfs)

    assert result == {"DoLo": [2]}
