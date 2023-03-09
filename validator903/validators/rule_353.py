import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="353",
        description="No episode submitted can start before 14 October 1991.",
        affected_fields=["DECOM"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]
            epi["DECOM"] = pd.to_datetime(
                epi["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            min_decom_allowed = pd.to_datetime(
                "14/10/1991", format="%d/%m/%Y", errors="coerce"
            )
            error_mask = epi["DECOM"] < min_decom_allowed
            return {"Episodes": epi.index[error_mask].to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"DECOM": pd.NA},  # 0
            {"DECOM": "02/06/1980"},  # 1   Fails
            {"DECOM": "06/06/1890"},  # 2   Fails
            {"DECOM": "08/06/2020"},  # 3
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2]}
