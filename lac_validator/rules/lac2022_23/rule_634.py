import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="634",
    message="There are entries for previous permanence options, but child has not started to be looked after from 1 April 2016 onwards.",
    affected_fields=["LA_PERM", "PREV_PERM", "DATE_PERM", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PrevPerm" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        prevperm = dfs["PrevPerm"]
        collection_start = dfs["metadata"]["collection_start"]
        # convert date field to appropriate format
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        collection_start = pd.to_datetime(
            collection_start, format="%d/%m/%Y", errors="coerce"
        )
        # the maximum date has the highest possibility of satisfying the condition
        episodes["LAST_DECOM"] = episodes.groupby("CHILD")["DECOM"].transform("max")

        # prepare to merge
        episodes.reset_index(inplace=True)
        prevperm.reset_index(inplace=True)
        merged = prevperm.merge(
            episodes, on="CHILD", how="left", suffixes=["_prev", "_eps"]
        )
        # If <PREV_PERM> or <LA_PERM> or <DATE_PERM> provided, then at least 1 episode must have a <DECOM> later than 01/04/2016
        mask = (
            merged["PREV_PERM"].notna()
            | merged["DATE_PERM"].notna()
            | merged["LA_PERM"].notna()
        ) & (merged["LAST_DECOM"] < collection_start)
        eps_error_locs = merged.loc[mask, "index_eps"]
        prevperm_error_locs = merged.loc[mask, "index_prev"]

        # return {'PrevPerm':prevperm_error_locs}
        return {
            "Episodes": eps_error_locs.unique().tolist(),
            "PrevPerm": prevperm_error_locs.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_prevperm = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "6", "7", "8"],
            "PREV_PERM": ["Z1", pd.NA, pd.NA, "Z1", pd.NA, "P1"],
            "LA_PERM": [pd.NA, "352", pd.NA, "352", pd.NA, "352"],
            "DATE_PERM": [pd.NA, pd.NA, "01/05/2000", pd.NA, pd.NA, "05/05/2020"],
            # last 3 rows will disappear after merging on CHILD
        }
    )
    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "101",
                "DECOM": "20/10/2011",
            },  # 0
            {
                "CHILD": "102",
                "DECOM": "19/11/2021",
            },  # 1
            {
                "CHILD": "102",
                "DECOM": "17/06/2001",
            },  # 2
            {
                "CHILD": "103",
                "DECOM": "04/04/2002",
            },  # 3
            {
                "CHILD": "103",
                "DECOM": "11/09/2015",
            },  # 4
            {
                "CHILD": "103",
                "DECOM": "01/03/2016",
            },  # 5
        ]
    )
    fake_dfs = {
        "PrevPerm": fake_data_prevperm,
        "Episodes": fake_data_episodes,
        "metadata": {"collection_start": "01/04/2016"},
    }

    result = validate(fake_dfs)

    assert result == {"PrevPerm": [0, 2], "Episodes": [0, 3, 4, 5]}
