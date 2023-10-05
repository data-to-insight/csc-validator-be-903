import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="207",
    message="Mother status for the current year disagrees with the mother status already recorded for this child.",
    affected_fields=["MOTHER"],
)
def validate(dfs):
    if "Header" not in dfs or "Header_last" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        header_last = dfs["Header_last"]
        episodes = dfs["Episodes"]

        header.reset_index(inplace=True)

        header_merged = header.merge(
            header_last,
            how="left",
            on=["CHILD"],
            suffixes=("", "_last"),
            indicator=True,
        )

        header_merged = header_merged.merge(
            episodes[["CHILD"]],
            on="CHILD",
            how="left",
            suffixes=("", "_eps"),
            indicator="_eps",
        )

        in_both_years = header_merged["_merge"] == "both"
        has_no_episodes = header_merged["_eps"] == "left_only"
        mother_is_different = header_merged["MOTHER"].astype(str) != header_merged[
            "MOTHER_last"
        ].astype(str)
        mother_was_true = header_merged["MOTHER_last"].astype(str) == "1"

        error_mask = (
            in_both_years & ~has_no_episodes & mother_is_different & mother_was_true
        )

        error_locations = list(header_merged.loc[error_mask, "index"].unique())

        return {"Header": error_locations}


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

    result = validate(fake_dfs)

    assert result == {"Header": [1, 3, 8]}
