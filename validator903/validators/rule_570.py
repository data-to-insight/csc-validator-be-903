import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="570",
        description="The date that the child started to be missing or away from placement without authorisation is after the end of the collection year.",
        affected_fields=["MIS_START"],
    )

    def _validate(dfs):
        if "Missing" not in dfs:
            return {}
        else:
            mis = dfs["Missing"]
            collection_end = pd.to_datetime(
                dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
            )

            mis["MIS_START"] = pd.to_datetime(
                mis["MIS_START"], format="%d/%m/%Y", errors="coerce"
            )
            error_mask = mis["MIS_START"] > collection_end

            return {"Missing": mis.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MIS_START": [
                "08/04/2020",
                "22/06/2020",
                pd.NA,
                "13/10/2005",
                "10/05/2001",
            ],
        }
    )

    metadata = {"collection_end": "31/03/2020"}

    fake_dfs = {"Missing": fake_data, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [0, 1]}
