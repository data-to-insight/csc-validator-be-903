import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="441",
    message="Participation method indicates child was 4 years old or over at the time of the review, but the date of birth and review date indicates the child was under 4 years old.",
    affected_fields=["DOB", "REVIEW", "REVIEW_CODE"],
)
def validate(dfs):
    if "Reviews" not in dfs:
        return {}
    else:
        reviews = dfs["Reviews"]
        reviews["DOB"] = pd.to_datetime(
            reviews["DOB"], format="%d/%m/%Y", errors="coerce"
        )
        reviews["REVIEW"] = pd.to_datetime(
            reviews["REVIEW"], format="%d/%m/%Y", errors="coerce"
        )
        reviews = reviews.dropna(subset=["REVIEW", "DOB"])

        mask = reviews["REVIEW_CODE"].isin(
            ["PN1", "PN2", "PN3", "PN4", "PN5", "PN6", "PN7"]
        ) & (reviews["REVIEW"] < reviews["DOB"] + pd.offsets.DateOffset(years=4))

        validation_error_mask = mask

        validation_error_locations = reviews.index[validation_error_mask]

        return {"Reviews": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DOB": [
                "01/01/2004",
                "01/01/2006",
                "01/01/2007",
                "01/01/2008",
                "01/01/2010",
                "01/01/2012",
                "01/01/2014",
                "01/06/2014",
            ],
            "REVIEW": [
                "31/12/2008",
                "01/01/2012",
                pd.NA,
                "01/01/2009",
                "01/01/2012",
                "01/01/2017",
                "01/01/2021",
                "01/01/2015",
            ],
            "REVIEW_CODE": ["PN1", "PN2", "PN3", "PN4", "PN5", "PN6", "PN7", "PN0"],
        }
    )

    fake_dfs = {"Reviews": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"Reviews": [3, 4]}
