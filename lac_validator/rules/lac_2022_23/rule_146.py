from validator903.types import ErrorDefinition


@rule_definition(
    code="146",
    message="Placement type code is not a valid code.",
    affected_fields=["PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    episodes = dfs["Episodes"]
    codelist = [
        "A3",
        "A4",
        "A5",
        "A6",
        "H5",
        "K1",
        "K2",
        "P1",
        "P2",
        "P3",
        "R1",
        "R2",
        "R3",
        "R5",
        "S1",
        "T0",
        "T1",
        "T2",
        "T3",
        "T4",
        "U1",
        "U2",
        "U3",
        "U4",
        "U5",
        "U6",
        "Z1",
    ]

    mask = episodes["PLACE"].isin(codelist) | episodes["PLACE"].isna()

    validationerrormask = ~mask
    validationerrorlocations = episodes.index[validationerrormask]

    return {"Episodes": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["A2", "R4", "Z", "P1", "", "t3", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 1, 2, 4, 5]}
