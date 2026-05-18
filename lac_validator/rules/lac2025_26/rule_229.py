import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="229",
    message="Placement provider does not match between the placing authority and the local authority code of "
    "the provider. [NOTE: The provider's LA code is inferred from the its postcode, and may "
    "be inaccurate in some cases.]",
    affected_fields=["URN", "PLACE_PROVIDER"],
    tables=["Episodes", "Provider Info"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("provider_info" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        provider_info = dfs["metadata"]["provider_info"]
        local_authority = dfs["metadata"]["localAuthority"]

        # merge
        episodes["index_eps"] = episodes.index
        episodes = episodes[
            episodes["URN"].notna()
            & (episodes["URN"] != "XXXXXXX")
            & ~episodes["PLACE"].isin(
                (
                    [
                        "K3",
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
                        "Z11",
                        "Z12",
                        "Z13",
                        "Z14",
                    ]
                )
            )
        ]
        merged = episodes.merge(provider_info, on="URN", how="left")

        # If Ofsted URN is provided and not 'XXXXXXX' and PL not in: 'K3', ‘P1’; ‘P3’; ‘R1’; ‘R2’; ‘R5’; ‘T0’; ‘T1’; ‘T2’; ‘T3’; ‘T4’; ‘Z11’; ‘Z12’; ‘Z13’; ‘Z14’
        # then: If <PLACE_PROVIDER> = 'PR1' then <LA> must equal Ofsted URN lookup <LA code>. If <PLACE_PROVIDER> = 'PR2' then Ofsted URN lookup <LA code> must not equal <LA>.
        mask = (
            merged["PLACE_PROVIDER"].eq("PR1")
            & merged["LA_CODE_INFERRED"].ne(local_authority)
        ) | (
            merged["PLACE_PROVIDER"].eq("PR2")
            & merged["LA_CODE_INFERRED"].eq(local_authority)
        )

        eps_error_locations = merged.loc[mask, "index_eps"].tolist()
        return {"Episodes": eps_error_locations}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR1",
                "PLACE": "X",
                "URN": 1,
            },  # 0 fail
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR2",
                "PLACE": "K3",
                "URN": pd.NA,
            },  # 1 ignore: URN is nan
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR2",
                "PLACE": "K3",
                "URN": 4,
            },  # 2 pass
            {
                "CHILD": "2222",
                "PLACE_PROVIDER": "PR1",
                "PLACE": "K3",
                "URN": "XXXXXXX",
            },  # 3 ignore: URN
            {
                "CHILD": "3333",
                "PLACE_PROVIDER": "PR2",
                "PLACE": "X",
                "URN": 2,
            },  # 4  fail
            {
                "CHILD": "3333",
                "PLACE_PROVIDER": "PR1",
                "PLACE": "K3",
                "URN": 2,
            },  # 5  pass
            {
                "CHILD": "4444",
                "PLACE_PROVIDER": "PR2",
                "PLACE": "K3",
                "URN": 3,
            },  # 6 pass
            {
                "CHILD": "5555",
                "PLACE_PROVIDER": "PR1",
                "PLACE": "X",
                "URN": 4,
            },  # 7 fail
            {
                "CHILD": "5555",
                "PLACE_PROVIDER": "PR2",
                "PLACE": "K3",
                "URN": 1,
            },  # 8 pass
            {
                "CHILD": "5555",
                "PLACE_PROVIDER": "PR1",
                "PLACE": "K3",
                "URN": 4,
            },  # 9 Pass
        ]
    )
    fake_provider_info = pd.DataFrame(
        [
            {
                "URN": 1,
                "LA_CODE_INFERRED": "other",
            },  # 0
            {
                "URN": 2,
                "LA_CODE_INFERRED": "auth",
            },  # 1
            {
                "URN": 3,
                "LA_CODE_INFERRED": "other",
            },  # 2
            {
                "URN": 4,
                "LA_CODE_INFERRED": pd.NA,
            },  # 3
        ]
    )
    metadata = {"localAuthority": "auth", "provider_info": fake_provider_info}

    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 4, 7]}
