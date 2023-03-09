import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="620",
        description="Child has been recorded as a mother, but date of birth shows that the mother is under 11 years of age.",
        affected_fields=["DOB", "MOTHER"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}
        else:
            hea = dfs["Header"]
            collection_start = pd.to_datetime(
                dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
            )
            hea["DOB"] = pd.to_datetime(hea["DOB"], format="%d/%m/%Y", errors="coerce")

            hea_mother = hea[hea["MOTHER"].astype(str) == "1"]
            error_cohort = (
                hea_mother["DOB"] + pd.offsets.DateOffset(years=11)
            ) > collection_start

            return {"Header": hea_mother.index[error_cohort].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_hea = pd.DataFrame(
        [
            {"MOTHER": "1", "DOB": pd.NA},  # 0
            {"MOTHER": "1", "DOB": "07/02/2020"},  # 1  Fails
            {"MOTHER": "1", "DOB": "03/02/2020"},  # 2  Fails
            {"MOTHER": pd.NA, "DOB": pd.NA},  # 3
            {"MOTHER": "1", "DOB": "18/01/1981"},  # 4  Passes old DOB
            {"MOTHER": "0", "DOB": "13/02/2020"},  # 5
        ]
    )

    metadata = {"collection_start": "01/04/2020"}

    fake_dfs = {"Header": fake_hea, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 2]}
