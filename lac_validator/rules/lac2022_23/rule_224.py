import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="224",
    message="The Ofsted Unique reference number (URN) provided for the child's placement does not match the placement provider recorded.",
    affected_fields=["PLACE_PROVIDER"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("provider_info" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        provider_info = dfs["metadata"]["provider_info"]

        # merge
        episodes["index_eps"] = episodes.index
        episodes = episodes[episodes["URN"].notna() & (episodes["URN"] != "XXXXXXX")]
        episodes = episodes.merge(
            provider_info, on="URN", how="left", suffixes=["_eps", "_lookup"]
        )
        # If <URN> provided and <URN> not = 'XXXXXXX', then <PLACE_PROVIDER> must = URN Lookup <PLACE_PROVIDER>
        valid = pd.Series(
            [
                (
                    pl_pr in valid.split(",")
                    if (pd.notna(pl_pr) and pd.notna(valid))
                    else False
                )
                for pl_pr, valid in zip(
                    episodes["PLACE_PROVIDER"], episodes["PROVIDER_CODES"]
                )
            ]
        )
        eps_error_locations = episodes.loc[~valid, "index_eps"]
        return {"Episodes": eps_error_locations.unique().tolist()}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR2",
                "URN": 1,
            },  # 0 fail
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR5",
                "URN": pd.NA,
            },  # 1 ignore
            {
                "CHILD": "1111",
                "PLACE_PROVIDER": "PR0",
                "URN": 3,
            },  # 2 fail
            {
                "CHILD": "2222",
                "PLACE_PROVIDER": "PR3",
                "URN": "XXXXXXX",
            },  # 3 ignore
            {
                "CHILD": "3333",
                "PLACE_PROVIDER": "PR0",
                "URN": 2,
            },  # 4 pass
            {
                "CHILD": "3333",
                "PLACE_PROVIDER": "PR3",
                "URN": 2,
            },  # 5 fail
            {
                "CHILD": "4444",
                "PLACE_PROVIDER": "PR3",
                "URN": 1,
            },  # 6 pass
            {
                "CHILD": "5555",
                "PLACE_PROVIDER": "PR3",
                "URN": 4,
            },  # 7 fail - if PROVIDER_CODES is null something is wrong
            {
                "CHILD": "5555",
                "PLACE_PROVIDER": "PR4",
                "URN": 1,
            },  # 8 pass
        ]
    )
    fake_provider_info = pd.DataFrame(
        [
            {
                "URN": 1,
                "PROVIDER_CODES": "PR1,PR3,PR4",
            },  # 0
            {
                "URN": 2,
                "PROVIDER_CODES": "PR0",
            },  # 1
            {
                "URN": 3,
                "PROVIDER_CODES": "PR1",
            },  # 2
            {
                "URN": 4,
                "PROVIDER_CODES": pd.NA,
            },  # 3
        ]
    )
    metadata = {"provider_info": fake_provider_info}

    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 2, 5, 7]}
