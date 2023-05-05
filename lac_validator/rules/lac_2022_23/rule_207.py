from validator903.types import ErrorDefinition


@rule_definition(
    code="207",
    message="Mother status for the current year disagrees with the mother status already recorded for this child.",
    affected_fields=["MOTHER"],
)
def validate(dfs):
    if "Header" not in dfs or "Headerlast" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        headerlast = dfs["Headerlast"]
        episodes = dfs["Episodes"]

        header.resetindex(inplace=True)

        headermerged = header.merge(
            headerlast,
            how="left",
            on=["CHILD"],
            suffixes=("", "last"),
            indicator=True,
        )

        headermerged = headermerged.merge(
            episodes[["CHILD"]],
            on="CHILD",
            how="left",
            suffixes=("", "eps"),
            indicator="eps",
        )

        inbothyears = headermerged["merge"] == "both"
        hasnoepisodes = headermerged["eps"] == "leftonly"
        motherisdifferent = headermerged["MOTHER"].astype(str) != headermerged[
            "MOTHERlast"
        ].astype(str)
        motherwastrue = headermerged["MOTHERlast"].astype(str) == "1"

        errormask = inbothyears & ~hasnoepisodes & motherisdifferent & motherwastrue

        errorlocations = list(headermerged.loc[errormask, "index"].unique())

        return {"Header": errorlocations}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "102",
                "103",
                "104",
                "105",
                "106",
                "108",
                "109",
                "110",
                "111",
            ],
            "MOTHER": ["1", 0, "1", pd.NA, pd.NA, "1", pd.NA, "0", "2", pd.NA],
        }
    )

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "102",
                "103",
                "104",
                "105",
                "107",
                "108",
                "109",
                "110",
                "111",
            ],
            "MOTHER": ["1", 1, "0", 1, pd.NA, "1", "0", pd.NA, "1", "1"],
        }
    )

    fake_episodes = pd.DataFrame(
        {
            "CHILD": [
                "101",
                "101",
                "102",
                "103",
                "104",
                "105",
                "106",
                "107",
                "108",
                "109",
                "110",
            ],
        }
    )

    fake_dfs = {
        "Header": fake_data,
        "Header_last": fake_data_prev,
        "Episodes": fake_episodes,
    }

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 3, 8]}
