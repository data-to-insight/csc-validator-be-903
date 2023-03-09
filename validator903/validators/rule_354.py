import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="354",
        description="Date episode ceased must be on or before the end of the current collection year.",
        affected_fields=["DECOM"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            collection_end = pd.to_datetime(
                dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
            )
            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            error_mask = epi["DECOM"] > collection_end
            error_list = epi.index[error_mask].to_list()
            return {"Episodes": error_list}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DECOM": [
                "01/01/2021",
                "19/02/2010",
                "38/04/2019",
                "01/01/2022",
                "01/04/2021",
                "01/05/2021",
                pd.NA,
                "3rd Dec 1873",
            ],
        }
    )

    metadata = {"collection_end": "01/04/2021"}

    fake_dfs = {"Episodes": fake_data, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 5]}
