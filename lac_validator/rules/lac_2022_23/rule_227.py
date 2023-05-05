import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="227",
    message="Ofsted Unique reference number (URN) is not valid for the episode start date.",
    affected_fields=["URN", "DECOM"],
)
def validate(dfs):
    if ("Episodes" not in dfs) or ("providerinfo" not in dfs["metadata"]):
        return {}
    else:
        episodes = dfs["Episodes"]
        providerinfo = dfs["metadata"]["providerinfo"]

        # convert date fields from strings to datetime format. NB. REGEND is in datetime format already.
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # merge
        episodes["indexeps"] = episodes.index
        episodes = episodes[episodes["URN"].notna() & (episodes["URN"] != "XXXXXXX")]
        merged = episodes.merge(providerinfo, on="URN", how="left")
        # If <URN> provided and <URN> not = 'XXXXXXX', then if <URN> and <REGEND> are provided then <DECOM> must be before <REGEND>
        mask = merged["REGEND"].notna() & (merged["DECOM"] >= merged["REGEND"])

        epserrorlocations = merged.loc[mask, "indexeps"]
        return {"Episodes": epserrorlocations.tolist()}


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
