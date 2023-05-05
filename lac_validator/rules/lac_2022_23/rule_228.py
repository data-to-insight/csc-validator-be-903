import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="228",
    message="Ofsted Unique reference number (URN) is not valid for the episode end date "
    "[NOTE: may give false positives on open episodes at providers who close during the year]",
    affected_fields=["URN", "DEC"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("provider_info" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        provider_info = dfs["metadata"]["provider_info"]
        collection_end = dfs["metadata"]["collection_end"]

        # convert date fields from strings to datetime format. NB. REG_END is in datetime format already.
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )

        # merge
        episodes["index_eps"] = episodes.index
        episodes = episodes[episodes["URN"].notna() & (episodes["URN"] != "XXXXXXX")]
        provider_info = provider_info[provider_info["REG_END"].notna()]

        merged = episodes.merge(provider_info, on="URN", how="inner")
        # If <URN> provided and not = 'XXXXXXX', and Ofsted URN <REG_END> not NULL then <DEC> if provided
        # must be <= Ofsted <REG_END>OR if not provided then<COLLECTION_END_DATE>must be<= <REG_END>.
        # Note: For open episodes (those without an end date) a check should be made to ensure that the Ofsted
        # URN was still open at the 31 March of the current year.
        mask = (merged["DEC"].notna() & (merged["DEC"] > merged["REG_END"])) | (
            merged["DEC"].isna() & (collection_end > merged["REG_END"])
        )

        eps_error_locations = merged.loc[mask, "index_eps"].sort_values().to_list()
        return {"Episodes": eps_error_locations}


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": "1111",
                "DEC": pd.NA,
                "URN": 1,
            },  # 0 pass REG_END is after March 31st of collection year
            {
                "CHILD": "1111",
                "DEC": "01/02/2015",
                "URN": pd.NA,
            },  # 1 ignore: URN not provided
            {
                "CHILD": "1111",
                "DEC": pd.NA,
                "URN": 3,
            },  # 2 fail REG_END is before March 31st of collection year
            {
                "CHILD": "2222",
                "DEC": "01/01/2010",
                "URN": "XXXXXXX",
            },  # 3 ignore: URN
            {
                "CHILD": "3333",
                "DEC": "01/01/2010",
                "URN": 2,
            },  # 4 pass
            {
                "CHILD": "3333",
                "DEC": "25/12/2015",
                "URN": 2,
            },  # 5 fail DEC after REG_END
            {
                "CHILD": "4444",
                "DEC": "25/12/2016",
                "URN": 1,
            },  # 6 fail. DEC after REG_END
            {
                "CHILD": "5555",
                "DEC": "01/01/2010",
                "URN": 4,
            },  # 7 ignore: REG_END is null
            {
                "CHILD": "5555",
                "DEC": "25/12/2015",
                "URN": 1,
            },  # 8 pass DEC equals REG_END
        ]
    )
    fake_provider_info = pd.DataFrame(
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
                "REG_END": "01/02/2015",
            },  # 2
            {
                "URN": 4,
                "REG_END": pd.NA,
            },  # 3
        ]
    )
    fake_provider_info["REG_END"] = pd.to_datetime(
        fake_provider_info["REG_END"], format="%d/%m/%Y", errors="raise"
    )
    metadata = {
        "collection_start": "01/04/2014",
        "collection_end": "31/03/2015",
        "provider_info": fake_provider_info,
    }

    fake_dfs = {"Episodes": fake_data_eps, "metadata": metadata}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 5, 6]}
