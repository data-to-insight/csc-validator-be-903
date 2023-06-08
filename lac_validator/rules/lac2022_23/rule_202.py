from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="202",
    message="The gender code conflicts with the gender already recorded for this child.",
    affected_fields=["SEX"],
)
def validate(dfs):
    if "Header" not in dfs or "Header_last" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        header_last = dfs["Header_last"]

        header_merged = (
            header.reset_index()
            .merge(
                header_last,
                how="left",
                on=["CHILD"],
                suffixes=("", "_last"),
                indicator=True,
            )
            .set_index("index")
        )

        in_both_years = header_merged["_merge"] == "both"
        sex_is_different = header_merged["SEX"].astype(str) != header_merged[
            "SEX_last"
        ].astype(str)

        error_mask = in_both_years & sex_is_different

        error_locations = header_merged.index[error_mask]

        return {"Header": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109", "110"],
            "SEX": ["1", 2, "1", "2", pd.NA, "1", pd.NA, "2", "3"],
        }
    )

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "107", "108", "109", "110"],
            "SEX": ["1", 1, "2", 2, pd.NA, "1", "2", pd.NA, "2"],
        }
    )

    fake_dfs = {"Header": fake_data, "Header_last": fake_data_prev}

    

    result = validate(fake_dfs)

    assert result == {"Header": [1, 2, 6, 7, 8]}
