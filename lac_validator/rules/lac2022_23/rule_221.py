import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="221",
    message="The Ofsted Unique reference number (URN) provided for the child's placement does not match the placement postcode provided.",
    affected_fields=["PL_POST"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("provider_info" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        provider_info = dfs["metadata"]["provider_info"]
        ls_list = ["V3", "V4"]
        place_list = ["K1", "K2", "R3", "S1"]
        xxx = "X" * 7
        # merge
        episodes["index_eps"] = episodes.index
        episodes = episodes[
            episodes["URN"].notna()
            & (episodes["URN"] != xxx)
            & (~episodes["LS"].isin(ls_list))
            & episodes["PLACE"].isin(place_list)
            & episodes["PL_POST"].notna()
        ]
        merged = episodes.merge(provider_info, on="URN", how="left")
        # If <URN> provided and <URN> not = 'XXXXXX', and <LS> not = 'V3', 'V4' and where <PL> = 'K1', 'K2', 'R3' or 'S1' and <PL_POST> provided, <PL_POST> should = URN Lookup <Provider Postcode>
        mask = merged["PL_POST"].str.replace(" ", "") != merged["POSTCODE"]

        eps_error_locations = merged.loc[mask, "index_eps"]
        return {"Episodes": eps_error_locations.unique().tolist()}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "LS": "V3",
                "PLACE": "R3",
                "PL_POST": "A11 5KE",
                "URN": 1,
            },  # 0 ignore: LS is V3
            {
                "CHILD": "1111",
                "LS": "V2",
                "PLACE": "R3",
                "PL_POST": "PR5",
                "URN": pd.NA,
            },  # 1 ignore: URN value
            {
                "CHILD": "1111",
                "LS": "V2",
                "PLACE": "K1",
                "PL_POST": "S25 1WO",
                "URN": 3,
            },  # 2 fail
            {
                "CHILD": "2222",
                "LS": "V2",
                "PLACE": "K2",
                "PL_POST": "PR3",
                "URN": "XXXXXXX",
            },  # 3 ignore: URN value
            {
                "CHILD": "3333",
                "LS": "V2",
                "PLACE": "R3",
                "PL_POST": "S25 1WO",
                "URN": 2,
            },  # 4 pass
            {
                "CHILD": "3333",
                "LS": "V2",
                "PLACE": "xx",
                "PL_POST": "S25 1WO",
                "URN": 2,
            },  # 5 ignore: PLACE value
            {
                "CHILD": "4444",
                "LS": "V2",
                "PLACE": "S1",
                "PL_POST": "N9 5PY",
                "URN": 1,
            },  # 6 fail
            {
                "CHILD": "5555",
                "LS": "V2",
                "PLACE": "S1",
                "PL_POST": "N9 5PY",
                "URN": 4,
            },  # 7 fail
            {
                "CHILD": "5555",
                "LS": "V2",
                "PLACE": "R3",
                "PL_POST": pd.NA,
                "URN": 1,
            },  # 8 ignore: PL_POST value
        ]
    )
    fake_provider_info = pd.DataFrame(
        [
            {
                "URN": 1,
                "POSTCODE": "A115KE",
            },  # 0
            {
                "URN": 2,
                "POSTCODE": "S251WO",
            },  # 1
            {
                "URN": 3,
                "POSTCODE": "V29XX",
            },  # 2
            {
                "URN": 4,
                "POSTCODE": pd.NA,
            },  # 3 should NaNs be ignored?
        ]
    )
    metadata = {"provider_info": fake_provider_info}

    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}

    result = validate(fake_dfs)

    assert result == {"Episodes": [2, 6, 7]}
