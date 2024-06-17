import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1008",
    message="Ofsted Unique Reference Number (URN) is not valid.",
    affected_fields=["URN"],
    tables=["Episodes", "Provider Info"],
)
def validate(dfs):
    if "Episodes" not in dfs or "provider_info" not in dfs["metadata"]:
        return {}
    else:
        episodes = dfs["Episodes"]
        providers = dfs["metadata"]["provider_info"]

        episodes["index_eps"] = episodes.index
        episodes = episodes[
            episodes["URN"].notna() & (episodes["URN"] != "XXXXXXX")
        ].copy()
        episodes["URN"] = episodes["URN"].astype(str)
        episodes = episodes.merge(providers, on="URN", how="left", indicator=True)
        mask = episodes["_merge"] == "left_only"
        eps_error_locations = episodes.loc[mask, "index_eps"]
        return {"Episodes": eps_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "URN": "SC999999",
            },  # 0 pass
            {
                "CHILD": "1111",
                "URN": pd.NA,
            },  # 1 ignore
            {
                "CHILD": "1111",
                "URN": 1234567,
            },  # 2 pass: digits will be converted to strings before comparison.
            {
                "CHILD": "2222",
                "URN": "XXXXXXX",
            },  # 3 pass: accepted placeholder value
            {
                "CHILD": "3333",
                "URN": "1234567",
            },  # 4 pass
            {
                "CHILD": "3333",
                "URN": "2345",
            },  # 5 fail
            {
                "CHILD": "4444",
                "URN": "999999",
            },  # 6 pass
            {
                "CHILD": "5555",
                "URN": "5b67891",
            },  # 7 fail
            {
                "CHILD": "5555",
                "URN": "XXXXXX",
            },  # 8 fail: 6 Xs instead of seven
        ]
    )

    metadata = {
        "provider_info": pd.DataFrame({"URN": ["1234567", "SC999999", "999999"]})
    }
    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Episodes": [5, 7, 8]}
