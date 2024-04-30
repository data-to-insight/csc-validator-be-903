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
        decom_before_dec_x1 = (
            (df["SW_DECOM"] <= df["DEC"]) | df["SW_DECOM"].isna()
        ) & (df["REC"] != "X1")
        swdecom_after_decom_s = (
            (df["SW_DECOM"] >= df["DECOM"]) | df["SW_DECOM"].isna()
        ) & (df["RNE"] == "S")
        not_V3_V4 = ~df["LS"].isin(["V3", "V4"])

        # If any of these are true, the child was not continously looked after
        not_continous = df[decom_before_dec_x1 | swdecom_after_decom_s | not_V3_V4]

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

        errors = not_continous[
            not_continous["SW_DECOM"].insa() & (not_continous["DEC_IN_YEAR"] == True)
        ]["CHILD"].tolist()

        error_rows = df[df["CHILD"].isin(errors)]

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    epi = pd.DataFrame(
        [
            {
                "CHILD": 1,
                "DECOM": 1,
                "DEC": 1,
            }
        ]
    )

    sw_eps = pd.DataFrame({"CHILD": 1, "SW_DECOM": pd.NA})

    metadata = {"collection_start": "01/04/2023", "collection_end": "31/03/2024"}

    fake_dfs = {"SWEpisodes": sw_eps, "Episodes": epi, "metadata": metadata}

    result = validate(fake_dfs)
