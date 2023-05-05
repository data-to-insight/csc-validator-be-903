import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="552",
    message="Date of Decision to place a child for adoption should be on or prior to the date that the child was placed for adoption.",
    # Field that defines date of decision to place a child for adoption is DATE_PLACED and the start of adoption is defined by DECOM with 'A' placement types.
    affected_fields=["DATE_PLACED", "DECOM"],
)
def validate(dfs):
    if ("PlacedAdoption" not in dfs) or ("Episodes" not in dfs):
        return {}
    else:
        # get the required datasets
        placedadoption = dfs["PlacedAdoption"]
        episodes = dfs["Episodes"]
        # keep index values so that they stay the same when needed later on for error locations
        placedadoption.resetindex(inplace=True)
        episodes.resetindex(inplace=True)

        adoptioneps = episodes[episodes["PLACE"].isin(["A3", "A4", "A5", "A6"])].copy()
        # find most recent adoption decision
        placedadoption["DATEPLACED"] = pd.todatetime(
            placedadoption["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        # remove rows where either of the required values have not been filled.
        placedadoption = placedadoption[placedadoption["DATEPLACED"].notna()]

        placedadoptioninds = placedadoption.groupby("CHILD")["DATEPLACED"].idxmax(
            skipna=True
        )
        lastdecision = placedadoption.loc[placedadoptioninds]

        # first time child started adoption
        adoptioneps["DECOM"] = pd.todatetime(
            adoptioneps["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        adoptioneps = adoptioneps[adoptioneps["DECOM"].notna()]

        adoptionepsinds = adoptioneps.groupby("CHILD")["DECOM"].idxmin(skipna=True)
        # full information of first adoption
        firstadoption = adoptioneps.loc[adoptionepsinds]

        # date of decision and date of start of adoption (DECOM) have to be put in one table
        merged = firstadoption.merge(
            lastdecision, on=["CHILD"], how="left", suffixes=["EP", "PA"]
        )

        # check to see if date of decision to place is less than or equal to date placed.
        decidedafterplaced = merged["DECOM"] < merged["DATEPLACED"]

        # find the corresponding location of error values per file.
        episodeerrorlocs = merged.loc[decidedafterplaced, "indexEP"]
        placedadoptionerrorlocs = merged.loc[decidedafterplaced, "indexPA"]

        return {
            "PlacedAdoption": placedadoptionerrorlocs.tolist(),
            "Episodes": episodeerrorlocs.tolist(),
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
                "baddate/2021",
            ],
            "CHILD": ["104", "105", "107", "108", "109", "110", "111"],
        }
    )
    fake_episodes = pd.DataFrame(
        {
            "DECOM": [
                "08/03/2020",
                "22/07/2020",
                "13/10/2021",
                "22/06/2020",
                "26/05/2018",
                pd.NA,
                "01/02/2013",
            ],
            "CHILD": ["104", "105", "107", "108", "109", "110", "111"],
            "PLACE": ["A3", "A4", "A6", "D5", "A3", "A5", "A4"],
        }
    )

    fake_dfs = {"PlacedAdoption": fake_placed_adoption, "Episodes": fake_episodes}
    # get the error function
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    # check that result of function on provided data is as expected
    assert result == {"PlacedAdoption": [2], "Episodes": [2]}
