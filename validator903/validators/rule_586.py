import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="586",
        description="Dates of missing periods are before child’s date of birth.",
        affected_fields=["MIS_START"],
    )

    def _validate(dfs):
        if "Missing" not in dfs:
            return {}
        else:
            df = dfs["Missing"]
            df["DOB"] = pd.to_datetime(df["DOB"], format="%d/%m/%Y", errors="coerce")
            df["MIS_START"] = pd.to_datetime(
                df["MIS_START"], format="%d/%m/%Y", errors="coerce"
            )

            error_mask = df["MIS_START"].notna() & (df["MIS_START"] <= df["DOB"])
            return {"Missing": df.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"DOB": "01/02/2020", "MIS_START": pd.NA},  # 0
            {"DOB": "02/02/2020", "MIS_START": "07/02/2020"},  # 1
            {"DOB": "04/02/2020", "MIS_START": "03/02/2020"},  # 2  Fails
            {"DOB": "06/02/2020", "MIS_START": pd.NA},  # 3
            {"DOB": "07/02/2020", "MIS_START": "01/02/2020"},  # 4  Fails
            {"DOB": "08/02/2020", "MIS_START": "13/02/2020"},  # 5
        ]
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Missing": [2, 4]}
