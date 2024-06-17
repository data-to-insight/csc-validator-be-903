import pandas as pd
import numpy as np

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW07STG2",
    message="Social worker episode end date should be on or after the start of the social worker reporting period, and should be on or before the collection end date.",
    affected_fields=["SW_DEC"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]
        collection_end = dfs["metadata"]["collection_end"]
        collection_end = pd.to_datetime(collection_end, format="%d/%m/%Y")

        collection_start = dfs["metadata"]["collection_start"]
        collection_start = pd.to_datetime(collection_start, format="%d/%m/%Y")

        df["SW_DEC"] = pd.to_datetime(df["SW_DEC"], format="%d/%m/%Y", errors="coerce")
        df = df[df["SW_DEC"].notna()].copy()

        error_rows = df[
            ~(df["SW_DEC"] >= (collection_start - np.timedelta64(1, "Y")))
            | ~(df["SW_DEC"] <= collection_end)
        ].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_DEC": ["01/04/2000", "31/03/1998", "01/01/2000", pd.NA],
        }
    )

    fake_meta = {"collection_end": "31/03/2000", "collection_start": "01/04/1999"}

    fake_dfs = {"SWEpisodes": fake_data, "metadata": fake_meta}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 1]}
