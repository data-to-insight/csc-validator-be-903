import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="523",
    message="Date of decision that the child should be placed for adoption should be the same date as the decision that adoption is in the best interest (date should be placed).",
    affected_fields=["DATE_PLACED", "DATE_INT"],
)
def validate(dfs):
    if ("AD1" not in dfs) or ("PlacedAdoption" not in dfs):
        return {}
    else:
        placedadoption = dfs["PlacedAdoption"]
        ad1 = dfs["AD1"]
        # keep initial index values to be reused for locating errors later on.
        placedadoption.resetindex(inplace=True)
        ad1.resetindex(inplace=True)

        # convert to datetime to enable comparison
        placedadoption["DATEPLACED"] = pd.todatetime(
            placedadoption["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        ad1["DATEINT"] = pd.todatetime(
            ad1["DATEINT"], format="%d/%m/%Y", errors="coerce"
        )

        # drop rows where either of the required values have not been filled.
        placedadoption = placedadoption[placedadoption["DATEPLACED"].notna()]
        ad1 = ad1[ad1["DATEINT"].notna()]

        # bring corresponding values together from both dataframes
        mergeddf = placedadoption.merge(
            ad1, on=["CHILD"], how="inner", suffixes=["AD", "PA"]
        )
        # find error values
        differentdates = mergeddf["DATEINT"] != mergeddf["DATEPLACED"]
        # map error locations to corresponding indices
        paerrorlocations = mergeddf.loc[differentdates, "indexPA"]
        ad1errorlocations = mergeddf.loc[differentdates, "indexAD"]

        return {
            "PlacedAdoption": paerrorlocations.tolist(),
            "AD1": ad1errorlocations.tolist(),
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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"AD1": [1, 2, 3], "PlacedAdoption": [1, 2, 3]}
