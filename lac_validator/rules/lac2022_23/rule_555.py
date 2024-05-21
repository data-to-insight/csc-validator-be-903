import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="555",
    message="Freeing order has been granted but there is no date of decision that the child should "
    + "be placed for adoption.",
    affected_fields=[
        "CHILD",
        "DATE_PLACED",
        "DATE_PLACED_CEASED",
        "REASON_PLACED_CEASED",
    ],
    tables=["Episodes", "PlacedAdoption"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        sho = dfs["PlacedAdoption"]
        sho.reset_index(inplace=True)
        epi.reset_index(inplace=True)

        # D1 episodes without a corresponding PlacedAdoption entry
        epi_has_d1 = epi[epi["LS"] == "D1"]
        merge_w_sho = epi_has_d1.merge(
            sho, how="left", on="CHILD", suffixes=["_EP", "_PA"], indicator=True
        )
        err_list_epi = (
            merge_w_sho.query("_merge == 'left_only'")["index_EP"].unique().tolist()
        )

        # Open D1 Episodes where DATE_PLACED_CEASED or REASON_PLACED_CEASED is filled in
        epi_open_d1 = epi[(epi["LS"] == "D1") & epi["DEC"].isna()]
        merge_w_sho2 = epi_open_d1.merge(
            sho, how="inner", on="CHILD", suffixes=["_EP", "_PA"]
        )
        err_list_sho = merge_w_sho2["index_PA"][
            merge_w_sho2["DATE_PLACED_CEASED"].notna()
            | merge_w_sho2["REASON_PLACED_CEASED"].notna()
        ]
        err_list_sho = err_list_sho.unique().tolist()
        return {"Episodes": err_list_epi, "PlacedAdoption": err_list_sho}


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "111", "LS": "E1", "DEC": "01/06/2020", "PLACE": "T3"},  # 0
            {"CHILD": "222", "LS": "D1", "DEC": "05/06/2020", "PLACE": "P3"},  # 1
            {"CHILD": "333", "LS": "D1", "DEC": "06/06/2020", "PLACE": "T3"},  # 2
            {
                "CHILD": "444",
                "LS": "D1",
                "DEC": pd.NA,
                "PLACE": "T3",
            },  # 3 Err not in sho
            {
                "CHILD": "555",
                "LS": "D1",
                "DEC": pd.NA,
                "PLACE": "T3",
            },  # 4 Err not in sho
            {"CHILD": "666", "LS": "D1", "DEC": pd.NA, "PLACE": "T3"},  # 5
        ]
    )
    fake_sho = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DATE_PLACED": "01/06/2020",
                "DATE_PLACED_CEASED": "01/06/2020",  # 0
                "REASON_PLACED_CEASED": "A",
            },
            {
                "CHILD": "222",
                "DATE_PLACED": "01/06/2020",
                "DATE_PLACED_CEASED": "01/06/2020",  # 1
                "REASON_PLACED_CEASED": "A",
            },
            {
                "CHILD": "333",
                "DATE_PLACED": "01/06/2020",
                "DATE_PLACED_CEASED": "01/06/2020",  # 2
                "REASON_PLACED_CEASED": "A",
            },
            {
                "CHILD": "666",
                "DATE_PLACED": "01/06/2020",
                "DATE_PLACED_CEASED": pd.NA,  # 3 err ceased not null
                "REASON_PLACED_CEASED": "A",
            },
            {
                "CHILD": "123",
                "DATE_PLACED": "01/06/2020",
                "DATE_PLACED_CEASED": "01/06/2020",  # 4
                "REASON_PLACED_CEASED": "A",
            },
            {
                "CHILD": "984",
                "DATE_PLACED": pd.NA,
                "DATE_PLACED_CEASED": "01/06/2020",  # 5
                "REASON_PLACED_CEASED": "A",
            },
        ]
    )
    fake_dfs = {"Episodes": fake_epi, "PlacedAdoption": fake_sho}

    result = validate(fake_dfs)

    assert result == {"Episodes": [3, 4], "PlacedAdoption": [3]}
