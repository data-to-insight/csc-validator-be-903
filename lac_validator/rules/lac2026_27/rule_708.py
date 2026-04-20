import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="708",
    message="Dates of DoLOs are before child’s date of birth.",
    affected_fields=["DOLO_START"],
    tables=["DoLo"],
)
def validate(dfs):
    # If <DOLO_START> not Null, then <DOLO_START> must be > <DOB>
    if "DoLo" not in dfs:
        return {}

    dolo = dfs["DoLo"]

    dolo["DOLO_START_dt"] = pd.to_datetime(
        dolo["DOLO_START"], format="%d/%m/%Y", errors="coerce"
    )

    dolo["DOB_dt"] = pd.to_datetime(dolo["DOB"], format="%d/%m/%Y", errors="coerce")

    has_start = dolo[dolo["DOLO_START"].notna()]

    error_rows = dolo[dolo["DOLO_START_dt"] <= dolo["DOB_dt"]].index

    return {"DoLo": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOLO_START": [
                "01/01/2000",
                pd.NA,
                "01/01/2000",
                "01/01/2000",
                "01/01/1999",
            ],
            "DOB": ["01/01/2000", "01/01/2000", pd.NA, "01/01/1999", "01/01/2000"],
        }
    )

    fake_dfs = {"DoLo": fake_data}

    result = validate(fake_dfs)

    assert result == {"DoLo": [0, 4]}
