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

        SWE["SW_DECOM"] = pd.to_datetime(
            SWE["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")

        epi = epi.reset_index()

        epi = epi[
            (~epi["LS"].isin(["V3", "V4"]))
            & ((epi["RNE"] == "S") | (epi["REC"] != "X1"))
        ]

        df = pd.merge(epi, SWE, how="left", on=["CHILD"])

        # finding episodes that start or end care and don't have a corresponding SWE episode
        swdecom_before_dec_nx1 = ((df["SW_DECOM"] <= df["DEC"])) & (df["REC"] != "X1")
        swdecom_after_decom_s = ((df["SW_DECOM"] >= df["DECOM"])) & (df["RNE"] == "S")

        error_rows = df[~swdecom_before_dec_nx1 & ~swdecom_after_decom_s]["index"]

        return {"Episodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    epi = pd.DataFrame(
        [
            {
                "CHILD": 1,
                "DECOM": "01/01/2024",
                "DEC": pd.NA,
                "REC": pd.NA,
                "RNE": "S",
                "LS": "C1",
            },  # Pass, has SW EP
            {
                "CHILD": 2,
                "DECOM": "01/01/2024",
                "DEC": pd.NA,
                "REC": pd.NA,
                "RNE": "S",
                "LS": "C1",
            },  # FAIL, no SW EP
            {
                "CHILD": 3,
                "DECOM": "01/01/2024",
                "DEC": pd.NA,
                "REC": pd.NA,
                "RNE": "S",
                "LS": "V4",
            },  # Pass, no SW EP but V4 (exempt)
            {
                "CHILD": 4,
                "DECOM": "01/01/2024",
                "DEC": "10/01/2024",
                "REC": "X1",
                "RNE": "P",
                "LS": "C1",
            },  # Pass, no SW EP but not a start or end placement
            {
                "CHILD": 4,
                "DECOM": "10/01/2024",
                "DEC": pd.NA,
                "REC": pd.NA,
                "RNE": "P",
                "LS": "C1",
            },  # Pass, no SW EP but not a start or end placement
            {
                "CHILD": 5,
                "DECOM": "01/01/2024",
                "DEC": "10/01/2024",
                "REC": "X1",
                "RNE": "S",
                "LS": "C1",
            },  # FAIL no SW EP (started after end)
            {
                "CHILD": 5,
                "DECOM": "10/01/2024",
                "DEC": "01/03/2024",
                "REC": "E4a",
                "RNE": "P",
                "LS": "C1",
            },  # Pass has SW EP
            {
                "CHILD": 6,
                "DECOM": "01/01/2024",
                "DEC": "10/01/2024",
                "REC": "X1",
                "RNE": "S",
                "LS": "C1",
            },  # Pass has SW EP
            {
                "CHILD": 6,
                "DECOM": "10/01/2024",
                "DEC": "01/03/2024",
                "REC": "E4a",
                "RNE": "P",
                "LS": "C1",
            },  # Pass has SW EP
            {
                "CHILD": 7,
                "DECOM": "01/04/2024",
                "DEC": pd.NA,
                "REC": "X1",
                "RNE": "S",
                "LS": "C1",
            },  # Edge case? FAIL but technically think should be fine if the SW_DEC (or no DEC) was after EPI DECOM (which we're not checking here)
        ]
    )

    sw_eps = pd.DataFrame(
        [
            {"CHILD": 1, "SW_DECOM": "01/01/2024"},
            {"CHILD": 5, "SW_DECOM": "01/02/2024"},
            {"CHILD": 6, "SW_DECOM": "01/02/2024"},
            {"CHILD": 7, "SW_DECOM": "01/02/2024"},
        ]
    )

    fake_dfs = {"SWEpisodes": sw_eps, "Episodes": epi}

    result = validate(fake_dfs)

    print(result)

    assert result == {"Episodes": [1, 4, 9]}
