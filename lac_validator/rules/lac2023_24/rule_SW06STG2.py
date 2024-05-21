import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW06STG2",
    message="Social worker episode data should be within the social worker data reporting year.",
    affected_fields=["SW_DECOM"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]
        collection_end = dfs["metadata"]["collection_end"]
        collection_end = pd.to_datetime(collection_end, format="%d/%m/%Y")

        df["SW_DECOM"] = pd.to_datetime(
            df["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        df = df[df["SW_DECOM"].notna()].copy()

        error_rows = df[~(df["SW_DECOM"] <= collection_end)].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_DECOM": ["01/04/2000", "31/03/2000", "01/01/2000", pd.NA],
        }
    )

    fake_meta = {"collection_end": "31/03/2000"}

    fake_dfs = {"SWEpisodes": fake_data, "metadata": fake_meta}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0]}
