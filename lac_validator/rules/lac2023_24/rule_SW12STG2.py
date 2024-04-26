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

        SWE["DECOM"] = pd.to_datetime(SWE["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")

        df["DEC_IN_YEAR"] = (df["DEC"] >= collection_start) & (
            df["DEC"] <= collection_end
        )

        df = pd.merge(epi, SWE, how="left", on="CHILD")

        # finding non-respite periods of care
        decom_before_dec_x1 = (df["SW_DECOM"] <= df["DEC"]) & (df["REC"] != "X1")
        decom_after_dec_s = (df["SW_DECOM"] >= df["DEC"]) & (df["RNE"] != "S")
        not_V3_V4 = ~df["LS"].isin(["V3", "V4"])

        # If any of these are true, the child was not continously looked after
        not_continous = decom_before_dec_x1 | decom_after_dec_s | not_V3_V4

        in_care_at_some_point = df.groupby("CHILD")["DEC_IN_YEAR"].transform("max")
        not_in_care_at_some_point = df.groupby("CHILD")[
            "implies_not_continuous"
        ].transform("max")

        # If CONTINOUSLY LOOKED AFTER == FALSE, there are previous episodes of care
        epi["CONTINUOUSLY_LOOKED_AFTER"] = (in_care_at_some_point == True) & (
            not_in_care_at_some_point == False
        )

        # finding failing rows, overwriting df variable
        df = pd.merge(epi, SWE, how="left", on="CHILD")

        swdecom_before_dec = df[df["SW_DECOM"] < df["DEC"]]["CHILD"].tolist()

        error_rows = df[
            (df["CONTINUOUSLY_LOOKED_AFTER"] == True)
            & ~(df["CHILD"].isin(swdecom_before_dec))
        ]["index"].tolist()

        return {"SWEpisodes": error_rows.tolist()}


# def test_validate():
#     import pandas as pd

#     fake_data = pd.DataFrame(
#         {
#             "SW_REASON": ["LAZINESS", "SWDIED", "SLEEPINESS", "CHCHAN"],
#         }
#     )

#     fake_dfs = {"SWEpisodes": fake_data}

#     result = validate(fake_dfs)

#     assert result == {"SWEpisodes": [0, 2]}
