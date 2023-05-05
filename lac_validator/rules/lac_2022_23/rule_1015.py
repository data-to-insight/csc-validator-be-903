from validator903.types import ErrorDefinition


@rule_definition(
    code="1015",
    message="Placement provider is own provision but child not placed in own LA.",
    affected_fields=["PL_LA"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        localauthority = dfs["metadata"]["localAuthority"]

        placementfosteringoradoption = df["PLACE"].isin(
            [
                "A3",
                "A4",
                "A5",
                "A6",
                "U1",
                "U2",
                "U3",
                "U4",
                "U5",
                "U6",
            ]
        )
        ownprovision = df["PLACEPROVIDER"].eq("PR1")
        isshortterm = df["LS"].isin(["V3", "V4"])
        isplla = df["PLLA"].eq(localauthority)

        checkedepisodes = ~placementfosteringoradoption & ~isshortterm & ownprovision
        checkedepisodes = checkedepisodes & df["LS"].notna() & df["PLACE"].notna()
        mask = checkedepisodes & ~isplla

        return {"Episodes": df.index[mask].tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"PLACE": "E1", "LS": "C1", "PLACE_PROVIDER": "PR1", "PL_LA": "auth"},
            {"PLACE": "E1", "LS": "C1", "PLACE_PROVIDER": "PR1", "PL_LA": "other"},
            {"PLACE": "U2", "LS": "C1", "PLACE_PROVIDER": "PR1", "PL_LA": "other"},
            {"PLACE": "E1", "LS": "V3", "PLACE_PROVIDER": "PR1", "PL_LA": "other"},
            {"PLACE": "E1", "LS": "C1", "PLACE_PROVIDER": "PR2", "PL_LA": "other"},
            {"PLACE": pd.NA, "LS": "C1", "PLACE_PROVIDER": "PR1", "PL_LA": "other"},
            {"PLACE": "E1", "LS": pd.NA, "PLACE_PROVIDER": "PR1", "PL_LA": "other"},
            {"PLACE": "E1", "LS": "C1", "PLACE_PROVIDER": pd.NA, "PL_LA": "other"},
        ]
    )

    metadata = {
        "localAuthority": "auth",
    }

    fake_dfs = {"Episodes": fake_data, "metadata": metadata}

    error_defn, error_func = validate()
    assert error_func(fake_dfs) == {"Episodes": [1]}
