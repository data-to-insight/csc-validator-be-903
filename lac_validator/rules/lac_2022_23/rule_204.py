from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="204",
    message="Ethnic origin code disagrees with the ethnic origin already recorded for this child.",
    affected_fields=["ETHNIC"],
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
        ethnic_is_different = (
            header_merged["ETHNIC"].astype(str).str.upper()
            != header_merged["ETHNIC_last"].astype(str).str.upper()
        )

        error_mask = in_both_years & ethnic_is_different

        error_locations = header.index[error_mask]

        return {"Header": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109", "110"],
            "ETHNIC": [
                "WBRI",
                "WBRI",
                "nobt",
                "AINS",
                pd.NA,
                "BOTH",
                pd.NA,
                "BCRB",
                "MWBC",
            ],
        }
    )

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "107", "108", "109", "110"],
            "ETHNIC": [
                "WBRI",
                "NOBT",
                "NOBT",
                "AINS",
                pd.NA,
                "REFU",
                "MOTH",
                pd.NA,
                "MWBA",
            ],
        }
    )

    fake_dfs = {"Header": fake_data, "Header_last": fake_data_prev}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 6, 7, 8]}
