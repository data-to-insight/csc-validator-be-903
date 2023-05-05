import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="440",
    message="Participation method indicates child was under 4 years old at the time of the review, but date of birth and review date indicates the child was 4 years old or over.",
    affected_fields=["DOB", "REVIEW", "REVIEW_CODE"],
)
def validate(dfs):
    if "Reviews" not in dfs:
        return {}
    else:
        reviews = dfs["Reviews"]
        reviews["DOB"] = pd.todatetime(
            reviews["DOB"], format="%d/%m/%Y", errors="coerce"
        )
        reviews["REVIEW"] = pd.todatetime(
            reviews["REVIEW"], format="%d/%m/%Y", errors="coerce"
        )

        mask = reviews["REVIEWCODE"].eq("PN0") & (
            reviews["REVIEW"] > reviews["DOB"] + pd.offsets.DateOffset(years=4)
        )

        validationerrormask = mask
        validationerrorlocations = reviews.index[validationerrormask]

        return {"Reviews": validationerrorlocations.tolist()}


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
            ],
            "REVIEW": [
                "31/12/2007",
                "01/01/2007",
                pd.NA,
                "01/01/2013",
                "01/01/2015",
                "01/01/2014",
                "01/01/2020",
            ],
            "REVIEW_CODE": ["PN0", "PN0", "PN0", "PN0", "PN0", "PN0", "PN1"],
        }
    )

    fake_dfs = {"Reviews": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Reviews": [3, 4]}
