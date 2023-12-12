import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="222",
    message="Ofsted Unique reference number (URN) should not be recorded for this placement type.",
    affected_fields=["URN"],
)
def validate(dfs):
    # If <URN> provided and <URN> not = ‘XXXXXX’, and where
    # <PL> = ‘P1’; ‘P3’; ‘R1’; ‘R2’; ‘R5’; ‘T0’ ‘T1’; ‘T2’; ‘T3’; ‘T4’ or Z1 then should not be provided
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        place_code_list = [
            "P1",
            "P3",
            "R1",
            "R2",
            "R5",
            "T0",
            "T1",
            "T2",
            "T3",
            "T4",
            "Z1",
        ]
        mask = (
            (df["PLACE"].isin(place_code_list))
            & (df["URN"].notna())
            & (df["URN"] != "XXXXXXX")
        )
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"PLACE": "H5", "URN": "XXXXXXX"},  # 0
            {"PLACE": "U1", "URN": "Whatever"},  # 1
            {"PLACE": "U2", "URN": pd.NA},  # 2
            {"PLACE": "T1", "URN": pd.NA},  # 3
            {"PLACE": "R1", "URN": "Whatever"},  # 4  Fail
            {"PLACE": "T2", "URN": "Whatever"},  # 5  Fail
            {"PLACE": "P2", "URN": "Whatever"},  # 6  Pass
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [4, 5]}
