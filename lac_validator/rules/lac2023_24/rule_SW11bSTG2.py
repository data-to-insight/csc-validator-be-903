import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW11bSTG2",
    message="Social worker episode has ended before 31 March and no subsequent social worker episode has been provided.",
    affected_fields=["SW_DEC"],
    tables=["SWEpisodes"],
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
            left_on=["index", "CHILD"],
            right_on=["level_0", "CHILD"],
            how="outer",
            suffixes=("", "_prev"),
        )

        m_df.dropna(subset="index", axis="rows", inplace=True)
        m_df["index"] = m_df["index"].astype("int")
        before_end = m_df[
            (m_df["SW_DEC_prev"] >= collection_end - pd.DateOffset(days=5))
        ]

        # If children only appear once and have a SW_DEC within 5 days of the collection end, they can't have a follow up SW_DECOM
        # non_m_df_before_end = df[df['SW_DEC'] >= collection_end - pd.DateOffset(days=5)]
        appearance_counts = df.value_counts("CHILD").reset_index()
        one_appearance = appearance_counts[appearance_counts[0] == 1]["CHILD"].tolist()
        children_appearing_once = df[df["CHILD"].isin(one_appearance)]["index"].tolist()

        pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        print(children_appearing_once)
        # different_child = before_end['CHILD'] != before_end['CHILD_prev']
        # same_child = before_end['CHILD'] == before_end['CHILD_prev']
        # error_rows = before_end[(before_end["SW_DECOM"].isna() & same_child) | (before_end['SW_DECOM_prev'].notna() & different_child)]["index"]

        error_rows = before_end[before_end["SW_DECOM"].isna()]["index"]
        error_rows = error_rows.to_list()
        error_rows.extend(children_appearing_once)
        return {"SWEpisodes": error_rows}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "1", "SW_DECOM": "01/04/2000", "SW_DEC": "26/03/2000"},
            {
                "CHILD": "1",
                "SW_DECOM": "01/05/2000",
                "SW_DEC": pd.NA,
            },  # Passes, rule doesn't suggest a timeframe needed for SW_DECOM
            {"CHILD": "2", "SW_DECOM": "01/04/2000", "SW_DEC": "25/03/2000"},
            {"CHILD": "2", "SW_DECOM": "02/04/2000", "SW_DEC": "03/04/2000"},
            {"CHILD": "3", "SW_DECOM": "01/04/2000", "SW_DEC": "1/04/2000"},
            {"CHILD": "3", "SW_DECOM": "02/04/2000", "SW_DEC": "03/04/2000"},
            {"CHILD": "4", "SW_DECOM": "01/04/2000", "SW_DEC": "30/03/2000"},
            {"CHILD": "4", "SW_DECOM": "30/03/2000", "SW_DEC": "03/04/2000"},
            {"CHILD": "5", "SW_DECOM": "01/04/2000", "SW_DEC": "30/03/2000"},
            {"CHILD": "6", "SW_DECOM": "01/04/2000", "SW_DEC": "26/03/2000"},
            {"CHILD": "6", "SW_DECOM": pd.NA, "SW_DEC": pd.NA},  # Fails, no SW_DECOM
            {"CHILD": "7", "SW_DECOM": "01/04/2000", "SW_DEC": "25/03/2000"},
            {
                "CHILD": "7",
                "SW_DECOM": pd.NA,
                "SW_DEC": pd.NA,
            },  # Passes, no SW_DEC outside of timeframe
            {"CHILD": "8", "SW_DECOM": "01/04/2000", "SW_DEC": "26/03/2000"},
            {"CHILD": "8", "SW_DECOM": "27/03/2000", "SW_DEC": "28/03/2000"},
            {
                "CHILD": "8",
                "SW_DECOM": pd.NA,
                "SW_DEC": pd.NA,
            },  # Fails, no SW_DECOM after DEC in timeframe
            {"CHILD": "9", "SW_DECOM": "01/03/2000", "SW_DEC": "25/03/2000"},
            {
                "CHILD": "9",
                "SW_DECOM": "26/03/2000",
                "SW_DEC": "27/03/2000",
            },  # Should fail, SW_DEC in timeframe no following DECOM
        ]
    )

    fake_meta = {"collection_end": "31/3/2000"}

    fake_dfs = {"SWEpisodes": fake_data, "metadata": fake_meta}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [10, 15, 8, 17]}
