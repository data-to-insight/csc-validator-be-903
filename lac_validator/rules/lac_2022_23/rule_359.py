import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="359",
    message="Child being looked after following 18th birthday must be accommodated under section 20(5) of the Children Act 1989 in a community home.",
    affected_fields=["DEC", "LS", "PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        hea = dfs["Header"]
        hea["DOB"] = pd.to_datetime(hea["DOB"], format="%d/%m/%Y", errors="coerce")
        collection_end = pd.to_datetime(
            dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
        )

        epi.reset_index(inplace=True)
        epi = epi.merge(hea, on="CHILD", how="left", suffixes=["", "_HEA"])

        mask_older_18 = (epi["DOB"] + pd.offsets.DateOffset(years=18)) < collection_end
        mask_null_dec = epi["DEC"].isna()
        mask_is_V2_K2 = (epi["LS"] == "V2") & (epi["PLACE"] == "K2")

        error_mask = mask_older_18 & mask_null_dec & ~mask_is_V2_K2
        error_list = epi["index"][error_mask].to_list()
        error_list = list(set(error_list))

        return {"Episodes": error_list}


def test_validate():
    import pandas as pd

    fake_hea = pd.DataFrame(
        [
            {"CHILD": "111", "DOB": "01/06/2020"},
            {"CHILD": "222", "DOB": "05/06/2000"},
            {"CHILD": "333", "DOB": "05/06/2000"},
            {"CHILD": "444", "DOB": "06/06/2000"},
            {"CHILD": "555", "DOB": "06/06/2019"},
        ]
    )

    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": "01/06/2020",
                "LS": "R1",
                "PLACE": "R2",
            },  # 0 DOB 01/06/2020
            {"CHILD": "222", "DEC": pd.NA, "LS": "V2", "PLACE": "K2"},
            # 1 DOB 05/06/2000 Passes older than 18, but has V2 K2
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "LS": "V2",
                "PLACE": "K1",
            },  # 2 DOB 05/06/2000 Fails
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "LS": "R1",
                "PLACE": "R2",
            },  # 3 DOB 06/06/2000 Fails
            {
                "CHILD": "555",
                "DEC": pd.NA,
                "LS": "R1",
                "PLACE": "R2",
            },  # 4 DOB 06/06/2019 Passes, Too young
        ]
    )

    metadata = {"collection_end": "31/03/2021"}

    fake_dfs = {"Header": fake_hea, "Episodes": fake_epi, "metadata": metadata}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 3]}
