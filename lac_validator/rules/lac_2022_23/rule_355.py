from validator903.types import ErrorDefinition


@rule_definition(
    code="355",
    message="Episode appears to have lasted for less than 24 hours",
    affected_fields=["DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        mask = df["DECOM"].astype(str) == df["DEC"].astype(str)
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DECOM": [
                "01/01/2000",
                "01/02/2000",
                "01/03/2000",
                "01/04/2000",
                "01/05/2000",
                "01/06/2000",
                "04/05/2000",
            ],
            "DEC": [
                "01/01/2000",
                "01/03/2000",
                pd.NA,
                "01/04/2000",
                "03/05/2000",
                "01/06/2000",
                "01/05/2000",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Episodes": [0, 3, 5]}
