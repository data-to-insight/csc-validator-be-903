import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="353",
    message="No episode submitted can start before 14 October 1991.",
    affected_fields=["DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        min_decom_allowed = pd.to_datetime(
            "14/10/1991", format="%d/%m/%Y", errors="coerce"
        )
        error_mask = epi["DECOM"] < min_decom_allowed
        return {"Episodes": epi.index[error_mask].to_list()}


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

    result = validate(fake_dfs)

    assert result == {"Episodes": [1, 2]}
