import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="382",
    message="A child receiving respite care cannot be in a temporary placement.",
    affected_fields=["LS", "PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        err_list = epi.query(
            "LS.isin(['V3', 'V4']) & PLACE.isin(['T0', 'T1', 'T2', 'T3', 'T4'])"
        ).index.tolist()
        return {"Episodes": err_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"PLACE": "T0", "LS": "V3"},  # 0
            {"PLACE": "R4", "LS": "V3"},  # 1
            {"PLACE": "T1", "LS": "X3"},  # 2
            {"PLACE": "T2", "LS": "V4"},  # 3
            {"PLACE": "T3", "LS": "V4"},  # 4
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 3, 4]}
