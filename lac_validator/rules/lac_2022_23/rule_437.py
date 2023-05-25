import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="437",
    message="Reason episode ceased is child has died or is aged 18 or over but there are further episodes.",
    affected_fields=["REC"],
)

# !# potential false negatives, as this only operates on the current year's data
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]

        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        episodes.sort_values(["CHILD", "DECOM"], inplace=True)
        episodes[["NEXT_DECOM", "NEXT_CHILD"]] = episodes[["DECOM", "CHILD"]].shift(-1)

        # drop rows with missing DECOM as invalid/missing values can lead to errors
        episodes = episodes.dropna(subset=["DECOM"])

        ceased_e2_e15 = episodes["REC"].str.upper().astype(str).isin(["E2", "E15"])
        has_later_episode = episodes["CHILD"] == episodes["NEXT_CHILD"]

        error_mask = ceased_e2_e15 & has_later_episode

        error_locations = episodes.index[error_mask]

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "102",
                "102",
                "103",
                "103",
                "103",
                "104",
                "104",
                "104",
                "104",
                "105",
                "105",
            ],
            "DECOM": [
                "20/10/2021",
                "19/11/2021",
                "17/06/2021",
                "04/04/2020",
                "11/09/2020",
                "07/05/2021",
                "15/02/2020",
                "09/04/2020",
                "24/09/2020",
                "30/06/2021",
                pd.NA,
                "20/12/2020",
            ],
            "REC": [
                "E2",
                "E15",
                "X1",
                "X1",
                "E15",
                pd.NA,
                "X1",
                "E4a",
                "X1",
                pd.NA,
                "E2",
                "X1",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data_episodes}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [4]}
