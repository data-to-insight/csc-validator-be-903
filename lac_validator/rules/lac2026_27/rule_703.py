import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="703",
    message="The date that the DoLO started is after the end of the collection year.",
    affected_fields=["DOLO_START"],
    tables=["DoLo"],
)
def validate(dfs):
    if "DoLo" not in dfs:
        return {}

    dolo = dfs["DoLo"]
    collection_end = dfs["metadata"]["collection_end"]

    dolo["DOLO_START_dt"] = pd.to_datetime(
        dolo["DOLO_START"], format="%d/%m/%Y", errors="coerce"
    )

    collection_end_dt = pd.to_datetime(
        collection_end, format="%d/%m/%Y", errors="coerce"
    )

    error_rows = dolo.index[(dolo["DOLO_START_dt"]) > collection_end_dt]

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
                "31/03/2000",
                "01/04/2000",
            ],
        }
    )

    metadata = {"collection_end": "31/03/2000"}

    fake_dfs = {"DoLo": fake_data, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"DoLo": [6]}
