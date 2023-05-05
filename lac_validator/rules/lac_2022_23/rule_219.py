import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="219",
    message="The Ofsted Unique reference number (URN) provided for the child's placement does not match the placement type recorded.",
    affected_fields=["URN", "PLACE"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("providerinfo" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        providerinfo = dfs["metadata"]["providerinfo"]

        # merge
        episodes["indexeps"] = episodes.index
        episodes = episodes[episodes["URN"].notna() & (episodes["URN"] != "XXXXXXX")]
        episodes = episodes.merge(providerinfo, on="URN", how="left")
        # If <URN> provided and <URN> not = 'XXXXXXX' then <PL> must = any URN Lookup <PLACEMENT CODE> of matching URN Lookup <URN>
        placevalid = pd.Series(
            [
                False if (pd.isna(pl) or pd.isna(valid)) else pl in valid.split(",")
                for pl, valid in zip(episodes["PLACE"], episodes["PLACECODES"])
            ]
        )

        epserrorlocations = episodes.loc[~placevalid, "indexeps"]
        return {"Episodes": epserrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "PLACE": "PR5",
                "URN": 1,
            },  # 0 fail
            {
                "CHILD": "1111",
                "PLACE": "PR5",
                "URN": pd.NA,
            },  # 1 ignore: URN
            {
                "CHILD": "1111",
                "PLACE": "PR7",
                "URN": 3,
            },  # 2 fail
            {
                "CHILD": "2222",
                "PLACE": "PR5",
                "URN": "XXXXXXX",
            },  # 3 ignore: URN
            {
                "CHILD": "3333",
                "PLACE": "PR1",
                "URN": 2,
            },  # 4 pass
            {
                "CHILD": "3333",
                "PLACE": "PR3",
                "URN": 2,
            },  # 5 pass
            {
                "CHILD": "4444",
                "PLACE": "PR5",
                "URN": 1,
            },  # 6 fail
            {
                "CHILD": "5555",
                "PLACE": "PR5",
                "URN": 4,
            },  # 7 fail - PLACE_CODES should not be null so probly needs a look
            {
                "CHILD": "5555",
                "PLACE": "PR2",
                "URN": 1,
            },  # 8 pass
        ]
    )
    fake_provider_info = pd.DataFrame(
        [
            {
                "URN": 1,
                "PLACE_CODES": "PR2",
            },  # 0
            {
                "URN": 2,
                "PLACE_CODES": "PR1,PR3,PR5",
            },  # 1
            {
                "URN": 3,
                "PLACE_CODES": "PR5,PR4,PR2",
            },  # 2
            {
                "URN": 4,
                "PLACE_CODES": pd.NA,
            },  # 3
        ]
    )
    metadata = {"provider_info": fake_provider_info}

    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 2, 6, 7]}
