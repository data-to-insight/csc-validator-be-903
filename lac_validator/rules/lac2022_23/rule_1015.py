import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1015",
    message="Placement provider is own provision but child not placed in own LA.",
    affected_fields=["PL_LA"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        local_authority = dfs["metadata"]["localAuthority"]

        placement_fostering_or_adoption = df["PLACE"].isin(
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
        own_provision = df["PLACE_PROVIDER"].eq("PR1")
        is_short_term = df["LS"].isin(["V3", "V4"])
        is_pl_la = df["PL_LA"].eq(local_authority)

        checked_episodes = (
            ~placement_fostering_or_adoption & ~is_short_term & own_provision
        )
        checked_episodes = checked_episodes & df["LS"].notna() & df["PLACE"].notna()
        mask = checked_episodes & ~is_pl_la

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

    assert validate(fake_dfs) == {"Episodes": [1]}
