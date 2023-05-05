from validator903.types import ErrorDefinition


@rule_definition(
    code="133",
    message="Data entry for accommodation after leaving care is invalid. If reporting on a childs accommodation after leaving care the data entry must be valid",
    affected_fields=["ACCOM"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}

    else:
        oc3 = dfs["OC3"]
        validcodes = [
            "B1",
            "B2",
            "C1",
            "C2",
            "D1",
            "D2",
            "E1",
            "E2",
            "G1",
            "G2",
            "H1",
            "H2",
            "K1",
            "K2",
            "R1",
            "R2",
            "S2",
            "T1",
            "T2",
            "U1",
            "U2",
            "V1",
            "V2",
            "W1",
            "W2",
            "X2",
            "Y1",
            "Y2",
            "Z1",
            "Z2",
            "0",
        ]

        errormask = ~oc3["ACCOM"].isin(validcodes)

        errorlocations = oc3.index[errormask]

        return {"OC3": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "ACCOM": ["B1", "B2", pd.NA, "S2", "K1", "X", "1"],
        }
    )

    fake_dfs = {"OC3": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [2, 5, 6]}
