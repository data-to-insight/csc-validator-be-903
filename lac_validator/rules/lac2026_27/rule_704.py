import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="704",
    message="The date that the DoLO ended is before the start or after the end of the collection year.",
    affected_fields=["DOLO_END"],
    tables=["DoLo"],
)
def validate(dfs):
    if "DoLo" not in dfs:
        return {}

    dolo = dfs["DoLo"]
    collection_end = dfs["metadata"]["collection_end"]
    collection_start = dfs["metadata"]["collection_start"]

    dolo["DOLO_END_dt"] = pd.to_datetime(
        dolo["DOLO_END"], format="%d/%m/%Y", errors="coerce"
    )

    collection_start_dt = pd.to_datetime(
        collection_start, format="%d/%m/%Y", errors="coerce"
    )

    collection_end_dt = pd.to_datetime(
        collection_end, format="%d/%m/%Y", errors="coerce"
    )

    error_rows = dolo.index[
        (dolo["DOLO_END_dt"] > collection_end_dt)
        | (dolo["DOLO_END_dt"] < collection_start_dt)
    ]

    return {"DoLo": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOLO_END": [
                "01/01/2000",
                "01/01/2000",
                pd.NA,
                "02/01/2000",
                "01/01/2000",
                "31/03/1999",
                "01/04/2000",
                "01/04/1999",
            ],
        }
    )

    metadata = {"collection_end": "31/03/2000", "collection_start": "01/04/1999"}

    fake_dfs = {"DoLo": fake_data, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"DoLo": [5, 6]}
