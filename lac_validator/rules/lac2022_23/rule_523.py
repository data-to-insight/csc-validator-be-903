import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="523",
    message="Date of decision that the child should be placed for adoption should be the same date as the decision that adoption is in the best interest (date should be placed).",
    affected_fields=["DATE_PLACED", "DATE_INT"],
    tables=["PlacedAdoption", "AD1"],
)
def validate(dfs):
    if ("AD1" not in dfs) or ("PlacedAdoption" not in dfs):
        return {}
    else:
        placed_adoption = dfs["PlacedAdoption"]
        ad1 = dfs["AD1"]
        # keep initial index values to be reused for locating errors later on.
        placed_adoption.reset_index(inplace=True)
        ad1.reset_index(inplace=True)

        # convert to datetime to enable comparison
        placed_adoption["DATE_PLACED"] = pd.to_datetime(
            placed_adoption["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
        )
        ad1["DATE_INT"] = pd.to_datetime(
            ad1["DATE_INT"], format="%d/%m/%Y", errors="coerce"
        )

        # drop rows where either of the required values have not been filled.
        placed_adoption = placed_adoption[placed_adoption["DATE_PLACED"].notna()]
        ad1 = ad1[ad1["DATE_INT"].notna()]

        # bring corresponding values together from both dataframes
        merged_df = placed_adoption.merge(
            ad1, on=["CHILD"], how="inner", suffixes=["_PA", "_AD"]
        )
        # find error values
        different_dates = merged_df["DATE_INT"] != merged_df["DATE_PLACED"]
        # map error locations to corresponding indices
        pa_error_locations = merged_df.loc[different_dates, "index_PA"]
        ad1_error_locations = merged_df.loc[different_dates, "index_AD"]

        return {
            "PlacedAdoption": pa_error_locations.to_list(),
            "AD1": ad1_error_locations.to_list(),
        }


def test_validate():
    import pandas as pd

    fake_placed_adoption = pd.DataFrame(
        {
            "DATE_PLACED": [
                "08/03/2020",
                "22/06/2020",
                "13/10/2022",
                "24/10/2021",
                pd.NA,
                pd.NA,
                "£1st/Februart",
                "11/11/2020",
            ],
            "CHILD": [1, 2, 3, 4, 5, 6, 7, 10],
        }
    )
    fake_ad1 = pd.DataFrame(
        {
            "DATE_INT": [
                "08/03/2020",
                "22/07/2020",
                "13/10/2021",
                "22/06/2020",
                "26/05/2018",
                pd.NA,
                "01/10/2020",
                "01/10/2020",
            ],
            "CHILD": [1, 2, 3, 4, 5, 6, 7, 333],
        }
    )

    fake_dfs = {"AD1": fake_ad1, "PlacedAdoption": fake_placed_adoption}

    # get the error function and run it on the fake data

    result = validate(fake_dfs)
    assert result == {"AD1": [1, 2, 3], "PlacedAdoption": [1, 2, 3]}
