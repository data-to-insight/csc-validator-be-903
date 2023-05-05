import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="620",
    message="Child has been recorded as a mother, but date of birth shows that the mother is under 11 years of age.",
    affected_fields=["DOB", "MOTHER"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        hea = dfs["Header"]
        collectionstart = pd.todatetime(
            dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
        )
        hea["DOB"] = pd.todatetime(hea["DOB"], format="%d/%m/%Y", errors="coerce")

        heamother = hea[hea["MOTHER"].astype(str) == "1"]
        errorcohort = (
            heamother["DOB"] + pd.offsets.DateOffset(years=11)
        ) > collectionstart

        return {"Header": heamother.index[errorcohort].tolist()}


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
