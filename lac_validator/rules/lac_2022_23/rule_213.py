from validator903.types import ErrorDefinition


@rule_definition(
    code="213",
    message="Placement provider information not required.",
    affected_fields=["PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        mask = (
            df["PLACE"].isin(["T0", "T1", "T2", "T3", "T4"])
            & df["PLACEPROVIDER"].notna()
        )
        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["T0", "U6", "U1", "U4", "P1", "T2", "T3", pd.NA, "Z1", "Z1"],
            "PLACE_PROVIDER": [
                pd.NA,
                pd.NA,
                "PR3",
                "PR4",
                "PR0",
                "PR2",
                "PR1",
                pd.NA,
                pd.NA,
                "notna",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [5, 6]}
