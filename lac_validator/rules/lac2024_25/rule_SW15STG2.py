import pandas as pd
import numpy as np

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW15STG2",
    message="Reason for social worker change is missing.",
    affected_fields=["SW_REASON"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]
        collection_start = dfs["metadata"]["collection_start"]
        collection_start = pd.to_datetime(collection_start, format="%d/%m/%Y")

        df["SW_DECOM"] = pd.to_datetime(
            df["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        reason_null = df[df["SW_REASON"].isna()]

        error_rows = reason_null[
            ~(reason_null["SW_DECOM"] < (collection_start - np.timedelta64(1, "Y")))
        ].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "SW_DECOM": "02/01/1999",
                "SW_REASON": pd.NA,
            },  # 0 fail no reason and less than a year old
            {
                "CHILD": "child2",
                "SW_DECOM": "02/01/1998",
                "SW_REASON": pd.NA,
            },  # 1 pass, over a year old
            {
                "CHILD": "child3",
                "SW_DECOM": "02/01/1999",
                "SW_REASON": "OTHERS",
            },  # pass, less than a year old but reason given
        ]
    )

    fake_meta = {"collection_start": "01/01/2000"}

    fake_dfs = {"SWEpisodes": fake_data, "metadata": fake_meta}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0]}
