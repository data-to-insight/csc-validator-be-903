import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1005",
    message="The end date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.",
    affected_fields=["MIS_END"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}
    else:
        missing = dfs["Missing"]
        missing["fMIS_END"] = pd.to_datetime(
            missing["MIS_END"], format="%d/%m/%Y", errors="coerce"
        )

        missing_end_date = missing["MIS_END"].isna()
        invalid_end_date = missing["fMIS_END"].isna()

        error_mask = ~missing_end_date & invalid_end_date

        error_locations = missing.index[error_mask]

        return {"Missing": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MIS_START": [
                "08/03/2020",
                "22/06/2020",
                pd.NA,
                "13/10/2021",
                "10/24/2021",
            ],
            "MIS_END": ["08/03/2020", pd.NA, "22/06/2020", "13/10/21", pd.NA],
        }
    )

    fake_dfs = {"Missing": fake_data}

    result = validate(fake_dfs)

    assert result == {"Missing": [3]}
