import pandas as pd

from lac_validator.rule_engine import rule_definition


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
        placed_adoption = dfs["PlacedAdoption"]
        episodes = dfs["Episodes"]
        # keep index values so that they stay the same when needed later on for error locations
        placed_adoption.reset_index(inplace=True)
        episodes.reset_index(inplace=True)

        adoption_eps = episodes[episodes["PLACE"].isin(["A3", "A4", "A5", "A6"])].copy()
        # find most recent adoption decision
        placed_adoption["DATE_PLACED"] = pd.to_datetime(
            placed_adoption["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
        )
        # remove rows where either of the required values have not been filled.
        placed_adoption = placed_adoption[placed_adoption["DATE_PLACED"].notna()]

        placed_adoption_inds = placed_adoption.groupby("CHILD")["DATE_PLACED"].idxmax(
            skipna=True
        )
        last_decision = placed_adoption.loc[placed_adoption_inds]

        # first time child started adoption
        adoption_eps["DECOM"] = pd.to_datetime(
            adoption_eps["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        adoption_eps = adoption_eps[adoption_eps["DECOM"].notna()]

        adoption_eps_inds = adoption_eps.groupby("CHILD")["DECOM"].idxmin(skipna=True)
        # full information of first adoption
        first_adoption = adoption_eps.loc[adoption_eps_inds]

        # date of decision and date of start of adoption (DECOM) have to be put in one table
        merged = first_adoption.merge(
            last_decision, on=["CHILD"], how="left", suffixes=["_EP", "_PA"]
        )

        # check to see if date of decision to place is less than or equal to date placed.
        decided_after_placed = merged["DECOM"] < merged["DATE_PLACED"]

        # find the corresponding location of error values per file.
        episode_error_locs = merged.loc[decided_after_placed, "index_EP"]
        placedadoption_error_locs = merged.loc[decided_after_placed, "index_PA"]

        return {
            "PlacedAdoption": placedadoption_error_locs.to_list(),
            "Episodes": episode_error_locs.to_list(),
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

    result = validate(fake_dfs)
    # check that result of function on provided data is as expected
    assert result == {"PlacedAdoption": [2], "Episodes": [2]}
