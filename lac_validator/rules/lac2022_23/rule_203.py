import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="203",
    message="Date of birth disagrees with the date of birth already recorded for this child.",
    affected_fields=["DOB"],
    tables=["Header", "Header_last"],
)
def validate(dfs):
    if "Header" not in dfs or "Header_last" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        header_last = dfs["Header_last"]

        header["DOB"] = pd.to_datetime(
            header["DOB"], format="%d/%m/%Y", errors="coerce"
        )
        header_last["DOB"] = pd.to_datetime(
            header_last["DOB"], format="%d/%m/%Y", errors="coerce"
        )

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
        dob_is_different = header_merged["DOB"].astype(str) != header_merged[
            "DOB_last"
        ].astype(str)

        error_mask = in_both_years & dob_is_different

        error_locations = header.index[error_mask]

        return {"Header": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "106", "108", "109", "110"],
            "DOB": [
                "16/03/2020",
                "23/09/2016",
                "31/12/19",
                "31/02/2018",
                pd.NA,
                "10/08/2014",
                pd.NA,
                "20/01/2017",
                "31/06/2020",
            ],
        }
    )

    fake_data_prev = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105", "107", "108", "109", "110"],
            "DOB": [
                "16/03/2020",
                "22/09/2016",
                "31/12/2019",
                "31/02/2018",
                pd.NA,
                "11/11/2021",
                "04/06/2017",
                pd.NA,
                "30/06/2020",
            ],
        }
    )

    fake_dfs = {"Header": fake_data, "Header_last": fake_data_prev}

    result = validate(fake_dfs)

    assert result == {"Header": [1, 2, 6, 7, 8]}
