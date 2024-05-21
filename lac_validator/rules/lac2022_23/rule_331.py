import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="331",
    message="Date of matching child and adopter(s) should be the same as, or prior to, the date of placement of adoption.",
    affected_fields=["DATE_MATCH", "DECOM", "REC"],  # AD1  # Episodes
    tables=["AD1", "Episodes"],
)
def validate(dfs):
    if "AD1" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        adt = dfs["AD1"]
        eps = dfs["Episodes"]

        # Save indexes of each table so we can retreive the original positions in each for our error rows
        adt["AD1_index"] = adt.index
        eps["Episodes_index"] = eps.index

        adt["DATE_MATCH"] = pd.to_datetime(
            adt["DATE_MATCH"], format="%d/%m/%Y", errors="coerce"
        )
        eps["DECOM"] = pd.to_datetime(eps["DECOM"], format="%d/%m/%Y", errors="coerce")

        # Only keep the episodes where <Adopted> = 'Y'
        adoption_eps = eps[eps["REC"].isin(["E11", "E12"])]

        # Merge AD1 and Episodes so we can compare DATE_MATCH and DECOM
        adoption_eps = adoption_eps.merge(adt, on="CHILD")

        # A child cannot be placed for adoption before the child has been matched with prospective adopter(s).
        error_mask = adoption_eps["DATE_MATCH"] > adoption_eps["DECOM"]

        # Get the rows of each table where the dates clash
        AD1_errs = list(adoption_eps.loc[error_mask, "AD1_index"].unique())
        Episodes_errs = list(adoption_eps.loc[error_mask, "Episodes_index"].unique())

        return {"AD1": AD1_errs, "Episodes": Episodes_errs}


def test_validate():
    import pandas as pd

    fake_adt = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "66"],
            "DATE_MATCH": [
                "01/01/2020",
                "02/06/2020",
                "11/11/2020",
                pd.NA,
                "01/02/2020",
                "04/06/2020",
            ],
        }
    )
    fake_eps = pd.DataFrame(
        {
            "CHILD": [
                "111",
                "222",
                "333",
                "444",
                "555",
                "555",
                "555",
                "66",
                "66",
                "66",
                "66",
            ],
            "DECOM": [
                "01/01/2020",
                "01/06/2020",
                "12/12/2020",
                "01/02/2020",
                "01/01/2020",
                "01/02/2020",
                "05/06/2020",
                "01/01/2020",
                "01/02/2020",
                "05/06/2020",
                "06/07/2020",
            ],
            "REC": [
                "E12",
                "E11",
                "E12",
                "E11",
                "xX",
                "E11",
                "E12",
                "Xx",
                "oO",
                "E11",
                "Oo",
            ],
        }
    )

    fake_dfs = {"AD1": fake_adt, "Episodes": fake_eps}

    result = validate(fake_dfs)

    assert result == {"AD1": [1], "Episodes": [1]}
