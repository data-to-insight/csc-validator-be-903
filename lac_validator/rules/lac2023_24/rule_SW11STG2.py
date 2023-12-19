import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW11STG2",
    message="Social worker episode has ended before 31 March and no subsequent social worker episode has been provided.",
    affected_fields=["SW_DECOM"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        df["SW_DEC"] = pd.to_datetime(df["SW_DEC"], format="%d/%m/%Y", errors="coerce")
        df["SW_DECOM"] = pd.to_datetime(
            df["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        collection_end = dfs["metadata"]["collection_end"]
        collection_end = pd.to_datetime(collection_end, format="%d/%m/%Y")

        df["index"] = df.index
        df = df.sort_values(["CHILD", "SW_DECOM"])

        df_lead = df.shift(1)
        df_lead = df_lead.reset_index()

        m_df = df.merge(
            df_lead,
            left_on="index",
            right_on="level_0",
            suffixes=("", "_prev"),
        )

        before_end = m_df[m_df["SW_DEC_prev"] < collection_end]

        error_rows = before_end[
            before_end["SW_DECOM"].isna()
            | (before_end["SW_DECOM"] != before_end["SW_DEC_prev"])
        ]["index"]

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "1", "SW_DECOM": "01/04/2000", "SW_DEC": "30/03/2000"},
            {"CHILD": "1", "SW_DECOM": pd.NA, "SW_DEC": pd.NA},
            {"CHILD": "2", "SW_DECOM": "01/04/2000", "SW_DEC": "30/03/2000"},
            {"CHILD": "2", "SW_DECOM": "02/04/2000", "SW_DEC": "03/04/2000"},
            {"CHILD": "3", "SW_DECOM": "01/04/2000", "SW_DEC": "1/04/2000"},
            {"CHILD": "3", "SW_DECOM": "02/04/2000", "SW_DEC": "03/04/2000"},
            {"CHILD": "4", "SW_DECOM": "01/04/2000", "SW_DEC": "30/03/2000"},
            {"CHILD": "4", "SW_DECOM": "30/03/2000", "SW_DEC": "03/04/2000"},
        ]
    )

    fake_meta = {"collection_end": "31/3/2000"}

    fake_dfs = {"SWEpisodes": fake_data, "metadata": fake_meta}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [1, 3]}
