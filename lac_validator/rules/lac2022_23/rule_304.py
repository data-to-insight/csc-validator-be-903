import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="304",
    message="Date unaccompanied asylum-seeking child (UASC) status ceased must be on or before the 18th birthday of a child.",
    affected_fields=["DUC"],
)
def validate(dfs):
    if "UASC" not in dfs:
        return {}
    else:
        uasc = dfs["UASC"]
        uasc["DOB"] = pd.to_datetime(uasc["DOB"], format="%d/%m/%Y", errors="coerce")
        uasc["DUC"] = pd.to_datetime(uasc["DUC"], format="%d/%m/%Y", errors="coerce")
        mask = uasc["DUC"].notna() & (
            uasc["DUC"] > uasc["DOB"] + pd.offsets.DateOffset(years=18)
        )

        return {"UASC": uasc.index[mask].to_list()}


def test_validate():
    import pandas as pd

    fake_uasc = pd.DataFrame(
        [
            {"DOB": "01/06/2000", "DUC": "05/06/2019"},  # 0 Fails
            {"DOB": "02/06/2000", "DUC": pd.NA},  # 1
            {"DOB": "03/06/2000", "DUC": "01/06/2015"},  # 2
            {"DOB": "04/06/2000", "DUC": "02/06/2020"},  # 3 Fails
            {"DOB": pd.NA, "DUC": "05/06/2020"},  # 4
        ]
    )

    fake_dfs = {"UASC": fake_uasc}

    result = validate(fake_dfs)

    assert result == {"UASC": [0, 3]}
