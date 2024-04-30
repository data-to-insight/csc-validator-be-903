import pandas as pd

from lac_validator.rule_engine import rule_definition
from lac_validator.utils import add_col_to_episodes_CONTINUOUSLY_LOOKED_AFTER


@rule_definition(
    code="SW12STG2",
    message="If a child is looked after on 31 March then all social worker episodes for the full previous year should be reported, even those whilst they were not looked after",
    affected_fields=["SW_DECOM"],
)
def validate(dfs):
    if ("SWEpisodes" not in dfs) | ("Episodes" not in dfs):
        return {}
    else:
        SWE = dfs["SWEpisodes"]
        epi = dfs["Episodes"]

        collection_start = pd.to_datetime(
            dfs["metadata"]["collection_start"], format="%d/%m/%Y"
        )
        collection_end = pd.to_datetime(
            dfs["metadata"]["collection_end"], format="%d/%m/%Y"
        )

        SWE["SW_DECOM"] = pd.to_datetime(
            SWE["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")

        # This assumes that missing SW Episodes are only ones not added to the end, not middle ones
        epi.sort_values(["CHILD", "DECOM"], ascending=True, inplace=True)
        epi["EPI_ID"] = epi.groupby("CHILD").cumcount()
        SWE.sort_values(["CHILD", "SW_DECOM"], ascending=True, inplace=True)
        SWE["EPI_ID"] = SWE.groupby("CHILD").cumcount()

        epi = epi[(epi["DEC"] >= collection_start) & (epi["DEC"] <= collection_end)]

        df = pd.merge(epi, SWE, how="left", on=["CHILD", "EPI_ID"])

        # finding non-respite periods of care
        swdecom_before_dec_x1 = (
            (df["SW_DECOM"] <= df["DEC"]) | df["SW_DECOM"].isna()
        ) & (df["REC"] != "X1")
        swdecom_after_decom_s = (
            (df["SW_DECOM"] >= df["DECOM"]) | df["SW_DECOM"].isna()
        ) & (df["RNE"] == "S")
        not_V3_V4 = ~df["LS"].isin(["V3", "V4"])

        # If any of these are true, the child was not continously looked after
        not_continous = df[swdecom_before_dec_x1 | swdecom_after_decom_s | not_V3_V4]

        # in_care_at_some_point = not_continous.groupby("CHILD")["DEC_IN_YEAR"].transform("max")
        # not_in_care_at_some_point = not_continous.groupby("CHILD")[
        #     "implies_not_continuous"
        # ].transform("max")

        # # If CONTINOUSLY LOOKED AFTER == FALSE, there are previous episodes of care
        # not_continous["CONTINUOUSLY_LOOKED_AFTER"] = (in_care_at_some_point == True) & (
        #     not_in_care_at_some_point == False
        # )

        # finding failing rows, overwriting df variable
        # df = pd.merge(epi, SWE, how="left", on="CHILD")

        # swdecom_before_dec = df[df["SW_DECOM"] < df["DEC"]]["CHILD"].tolist()

        # error_rows = df[
        #     (df["CONTINUOUSLY_LOOKED_AFTER"] == True)
        #     & ~(df["CHILD"].isin(swdecom_before_dec))
        # ]["index"].tolist()

        # not_continous.sort_values(["CHILD", "DECOM", "SW_DECOM"], ascending=[True, True, True], inplace=True)
        # print(not_continous)
        # not_continous.drop_duplicates(["CHILD", "SW_DECOM"], inplace=True, keep="first")
        # print(not_continous)

        # Ensuring we only send rows for which there is no SW Episode
        # decom_after_dec = not_continous[not_continous['SW_DECOM'] > not_continous["DEC"]]

        # print(decom_after_dec)

        error_rows = not_continous[not_continous["SW_DECOM"].isna()].index

        # error_rows = df[df["CHILD"].isin(errors)].index

        return {"Episodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    epi = pd.DataFrame(
        [
            {
                "CHILD": 1,
                "DECOM": "01/01/2024",
                "DEC": "01/02/2024",
                "REC": "Q",
                "RNE": "Q",
                "LS": "Q",
            },  # Pass, has SW EP
            {
                "CHILD": 1,
                "DECOM": "02/02/2024",
                "DEC": "01/03/2024",
                "REC": "Q",
                "RNE": "Q",
                "LS": "Q",
            },  # Pass has SW EP
            {
                "CHILD": 1,
                "DECOM": "02/03/2024",
                "DEC": "03/03/2024",
                "REC": "Q",
                "RNE": "Q",
                "LS": "Q",
            },  # FAIL, no SW EP
            {
                "CHILD": 1,
                "DECOM": "04/03/2024",
                "DEC": pd.NA,
                "REC": "Q",
                "RNE": "Q",
                "LS": "Q",
            },  # Pass, not closed?
            {
                "CHILD": 2,  # passes, no dec inyear
                "DECOM": "01/01/2024",
                "DEC": pd.NA,
                "REC": pd.NA,
                "RNE": pd.NA,
                "LS": pd.NA,
            },
        ]
    )

    sw_eps = pd.DataFrame(
        [
            {"CHILD": 1, "SW_DECOM": "01/01/2024"},
            {"CHILD": 1, "SW_DECOM": "02/02/2024"},
        ]
    )

    metadata = {"collection_start": "01/04/2023", "collection_end": "31/03/2024"}

    fake_dfs = {"SWEpisodes": sw_eps, "Episodes": epi, "metadata": metadata}

    result = validate(fake_dfs)

    print(result)

    assert result == {"Episodes": [2]}
