from validator903.types import ErrorDefinition


@rule_definition(
    code="229",
    message="Placement provider does not match between the placing authority and the local authority code of "
    "the provider. [NOTE: The provider's LA code is inferred from the its postcode, and may "
    "be inaccurate in some cases.]",
    affected_fields=["URN", "PLACE_PROVIDER"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("providerinfo" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        providerinfo = dfs["metadata"]["providerinfo"]
        localauthority = dfs["metadata"]["localAuthority"]

        # merge
        episodes["indexeps"] = episodes.index
        episodes = episodes[episodes["URN"].notna() & (episodes["URN"] != "XXXXXXX")]
        merged = episodes.merge(providerinfo, on="URN", how="left")

        # If Ofsted URN is provided and not 'XXXXXXX' then: If <PLACEPROVIDER> = 'PR1' then <LA> must equal Ofsted URN lookup <LA code>. If <PLACEPROVIDER> = 'PR2' then Ofsted URN lookup <LA code> must not equal <LA>.
        mask = (
            merged["PLACEPROVIDER"].eq("PR1")
            & merged["LACODEINFERRED"].ne(localauthority)
        ) | (
            merged["PLACEPROVIDER"].eq("PR2")
            & merged["LACODEINFERRED"].eq(localauthority)
        )

        epserrorlocations = merged.loc[mask, "indexeps"].tolist()
        return {"Episodes": epserrorlocations}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR1",
                "URN": 1,
            },  # 0 fail
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR2",
                "URN": pd.NA,
            },  # 1 ignore: URN is nan
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR2",
                "URN": 4,
            },  # 2 pass
            {
                "CHILD": "2222",
                "PLACE_PROVIDER": "PR1",
                "URN": "XXXXXXX",
            },  # 3 ignore: URN
            {
                "CHILD": "3333",
                "PLACE_PROVIDER": "PR2",
                "URN": 2,
            },  # 4  fail
            {
                "CHILD": "3333",
                "PLACE_PROVIDER": "PR1",
                "URN": 2,
            },  # 5  pass
            {
                "CHILD": "4444",
                "PLACE_PROVIDER": "PR2",
                "URN": 3,
            },  # 6 pass
            {
                "CHILD": "5555",
                "PLACE_PROVIDER": "PR1",
                "URN": 4,
            },  # 7 fail
            {
                "CHILD": "5555",
                "PLACE_PROVIDER": "PR2",
                "URN": 1,
            },  # 8 pass
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
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 4, 7]}
