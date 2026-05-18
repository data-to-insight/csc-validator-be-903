import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="242",
    message="URN = 'XXXXXXX' can only be used for regional adoption agencies",
    affected_fields=["URN"],
    tables=["Episodes"],
)
def validate(dfs):
    # If <URN> = 'XXXXXXX' then <PL> must be in ('A3, 'A4', 'A5', 'A6', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6')
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        place_code_list = ["A3", "A4", "A5", "A6", "U1", "U2", "U3", "U4", "U5", "U6"]

        # XXXXXXX rows without an allowed PLACE code
        mask = (df["URN"] == "XXXXXXX") & ~(df["PLACE"].isin(place_code_list))
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "URN": "XXXXXXX",
                "PLACE": "A3",
            },  # 0
            {
                "URN": "XXXXXXX",
                "PLACE": "K3",
            },  # 1 FAILS
            {
                "URN": "URNURN",
                "PLACE": "A3",
            },  # 2
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [1]}
