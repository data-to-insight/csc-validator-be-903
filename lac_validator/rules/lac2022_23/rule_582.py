import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="582",
    message="Child is showing as ceasing to be looked after due to adoption, but the date of adoption is the same as the date reported for being matched with adopters. In most circumstances we expect the date the child is matched with adopters to be before the date of adoption.",
    affected_fields=["DEC", "DATE_MATCH"],
    tables=["Episodes", "AD1"],
)
def validate(dfs):
    # If <REC> = 'E11' or 'E12' then that episode <DEC> should not = <DATE_MATCH>
    # Apply for 2023 onwards
    if "Episodes" not in dfs or "AD1" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        ad1 = dfs["AD1"]

        episodes = episodes.reset_index()

        rec_codes = ["E11", "E12"]

        episodes = episodes[episodes["REC"].isin(rec_codes)]

        merged_df = episodes.merge(ad1, how="left", on="CHILD").set_index("index")

        episodes_with_errors = merged_df[merged_df["DEC"] == merged_df["DATE_MATCH"]]

        error_mask = episodes.index.isin(episodes_with_errors.index)

        error_locations = episodes.index[error_mask]

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I"],
            "REC": ["x", "E11", "E12", "E11", "E12", "E11", "E12", "E11", "E11", "A3"],
            "DEC": [
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
                "01/01/2020",
            ],
        }
    )
    fake_data_ad1 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "DATE_MATCH": [
                pd.NA,
                "02/01/2020",
                "02/01/2020",
                "02/01/2020",
                "02/01/2020",
                "02/01/2020",
                "02/01/2020",
                "01/01/2020",
            ],
        }
    )

    fake_dfs = {
        "Episodes": fake_data_episodes,
        "AD1": fake_data_ad1,
    }

    result = validate(fake_dfs)

    assert result == {"Episodes": [8]}
