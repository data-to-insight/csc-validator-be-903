import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="571",
    message="The date that the child ceased to be missing or away from placement without authorisation is before the start or after the end of the collection year.",
    affected_fields=["MIS_END"],
    tables=["Missing"],
)
def validate(dfs):
    if "Missing" not in dfs:
        return {}
    else:
        missing = dfs["Missing"]
        collection_start = pd.to_datetime(
            dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
        )
        collection_end = pd.to_datetime(
            dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
        )

        missing["fMIS_END"] = pd.to_datetime(
            missing["MIS_END"], format="%d/%m/%Y", errors="coerce"
        )

        end_date_before_year = missing["fMIS_END"] < collection_start
        end_date_after_year = missing["fMIS_END"] > collection_end

        error_mask = end_date_before_year | end_date_after_year

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

    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2020"}

    fake_dfs = {"Missing": fake_data, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Missing": [0, 2]}
