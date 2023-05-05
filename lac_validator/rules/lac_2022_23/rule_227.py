import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="227",
    message="Ofsted Unique reference number (URN) is not valid for the episode start date.",
    affected_fields=["URN", "DECOM"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("provider_info" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        provider_info = dfs["metadata"]["provider_info"]

        # convert date fields from strings to datetime format. NB. REG_END is in datetime format already.
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # merge
        episodes["index_eps"] = episodes.index
        episodes = episodes[episodes["URN"].notna() & (episodes["URN"] != "XXXXXXX")]
        merged = episodes.merge(provider_info, on="URN", how="left")
        # If <URN> provided and <URN> not = 'XXXXXXX', then if <URN> and <REG_END> are provided then <DECOM> must be before <REG_END>
        mask = merged["REG_END"].notna() & (merged["DECOM"] >= merged["REG_END"])

        eps_error_locations = merged.loc[mask, "index_eps"]
        return {"Episodes": eps_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "DECOM": "01/01/2014",
                "URN": 1,
            },  # 0 pass
            {
                "CHILD": "1111",
                "DECOM": "01/02/2015",
                "URN": pd.NA,
            },  # 1 ignore: URN not provided
            {
                "CHILD": "1111",
                "DECOM": "01/01/2016",
                "URN": 3,
            },  # 2 pass
            {
                "CHILD": "2222",
                "DECOM": "01/01/2010",
                "URN": "XXXXXXX",
            },  # 3 ignore
            {
                "CHILD": "3333",
                "DECOM": "01/01/2010",
                "URN": 2,
            },  # 4 pass
            {
                "CHILD": "3333",
                "DECOM": "25/12/2015",
                "URN": 2,
            },  # 5 fail DECOM after REG_END
            {
                "CHILD": "4444",
                "DECOM": "25/12/2016",
                "URN": 1,
            },  # 6 fail. DECOM after REG_END
            {
                "CHILD": "5555",
                "DECOM": "01/01/2010",
                "URN": 4,
            },  # 7 ignore: REG_END not provided
            {
                "CHILD": "5555",
                "DECOM": "25/12/2015",
                "URN": 1,
            },  # 8 fail DECOM equals REG_END
        ]
    )
    provider_info = pd.DataFrame(
        [
            {
                "URN": 1,
                "REG_END": "25/12/2015",
            },  # 0
            {
                "URN": 2,
                "REG_END": "21/02/2014",
            },  # 1
            {
                "URN": 3,
                "REG_END": "25/12/2017",
            },  # 2
            {
                "URN": 3,
                "REG_END": pd.NA,
            },  # 3
        ]
    )
    provider_info["REG_END"] = pd.to_datetime(
        provider_info["REG_END"], format="%d/%m/%Y", errors="coerce"
    )

    metadata = {"provider_info": provider_info}

    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Episodes": [5, 6, 8]}
