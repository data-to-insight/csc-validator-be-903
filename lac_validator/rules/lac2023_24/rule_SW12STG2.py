import pandas as pd

from lac_validator.rule_engine import rule_definition


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

        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")

        SWE["DECOM"] = pd.to_datetime(SWE["DECOM"], format="%d/%m/%Y", errors="coerce")

        collection_start = pd.to_datetime(
            dfs["metadata"]["collection_start"], format="%d/%m/%Y"
        )
        collection_end = pd.to_datetime(
            dfs["metadata"]["collection_end"], format="%d/%m/%Y"
        )

        non_respite_poc = epi[
            ~epi["LS"].isin(["V3", "V4"])
            & (epi["DEC"] >= collection_start)
            & (epi["DEC"] <= collection_end)
        ]

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
