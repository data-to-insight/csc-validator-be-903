import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="392b",
    message="Child is looked after but no postcodes are recorded. [NOTE: This check may result in false "
    "positives for children formerly UASC, particularly if current & prior year UASC data not loaded]",
    affected_fields=["HOME_POST", "PL_POST"],
)
def validate(dfs):
    # Will also use Header/UASC and/or Header_last/UASC_last for former UASC status
    if "Episodes" not in dfs:
        return {}
    else:
        # If <LS> not = 'V3' or 'V4' and <UASC> = '0' and <COLLECTION YEAR> - 1 <UASC> = '0' and <COLLECTION YEAR> - 2 <UASC> = '0' then <HOME_POST> and <PL_POST> should be provided.
        epi = dfs["Episodes"]
        epi["original_index"] = epi.index

        # Remove any children with evidence of former UASC status
        header = pd.DataFrame()
        if "Header" in dfs:
            header_current = dfs["Header"]
            header = pd.concat((header, header_current), axis=0)
        elif "UASC" in dfs:
            uasc = dfs["UASC"]
            uasc = uasc.loc[
                uasc.drop("CHILD", axis="columns").notna().any(axis=1), ["CHILD"]
            ].copy()
            uasc.loc[:, "UASC"] = "1"
            header = pd.concat((header, uasc), axis=0)

        if "Header_last" in dfs:
            header = pd.concat((header, dfs["Header_last"]), axis=0)
        elif "UASC_last" in dfs:
            uasc = dfs["UASC_last"]
            uasc = uasc.loc[
                uasc.drop("CHILD", axis="columns").notna().any(axis=1), ["CHILD"]
            ].copy()
            uasc.loc[:, "UASC"] = "1"
            header = pd.concat((header, uasc), axis=0)

        if "UASC" in header.columns:
            header = header[header.UASC == "1"].drop_duplicates("CHILD")
            epi = epi.merge(
                header[["CHILD"]], how="left", on="CHILD", indicator=True
            ).query("_merge == 'left_only'")

        # Remove episodes where LS is V3/V4
        epi = epi.query("(~LS.isin(['V3','V4']))")

        # Remove episodes with postcodes filled in
        epi = epi.query("(HOME_POST.isna() | PL_POST.isna())")

        # Get error indices
        err_list = epi["original_index"].sort_values().tolist()

        return {"Episodes": err_list}


def test_validate():
    import pandas as pd

    fake_episodes = pd.DataFrame(
        [
            {"CHILD": "111", "LS": "L1", "HOME_POST": "XX1", "PL_POST": "XX1"},  # 0
            {"CHILD": "222", "LS": "L1", "HOME_POST": "XX1", "PL_POST": pd.NA},  # 1
            {"CHILD": "222", "LS": "V3", "HOME_POST": pd.NA, "PL_POST": "XX1"},  # 2
            {"CHILD": "333", "LS": "L1", "HOME_POST": "XX1", "PL_POST": pd.NA},  # 3
            {"CHILD": "333", "LS": "V4", "HOME_POST": "XX1", "PL_POST": "XX1"},  # 4
            {"CHILD": "345", "LS": "L1", "HOME_POST": "XX1", "PL_POST": pd.NA},  # 5
            {"CHILD": "444", "LS": "L1", "HOME_POST": "XX1", "PL_POST": "XX1"},  # 6
            {"CHILD": "444", "LS": "V3", "HOME_POST": pd.NA, "PL_POST": pd.NA},  # 7
        ]
    )

    fake_header = pd.DataFrame(
        [
            {"CHILD": "111", "UASC": "1"},  # 0
            {"CHILD": "222", "UASC": "0"},  # 2
            {"CHILD": "333", "UASC": "0"},  # 4
            {"CHILD": "345", "UASC": "0"},  # 5
            {"CHILD": "444", "UASC": "0"},  # 6
        ]
    )
    fake_header_last = pd.DataFrame(
        [
            {"CHILD": "111", "UASC": "0"},  # 0
            {"CHILD": "222", "UASC": "0"},  # 2
            {"CHILD": "333", "UASC": "0"},  # 4
            {"CHILD": "345", "UASC": "0"},  # 5
            {"CHILD": "444", "UASC": "1"},  # 6
        ]
    )

    fake_dfs = {
        "Episodes": fake_episodes,
        "Header": fake_header,
        "Header_last": fake_header_last,
    }

    result = validate(fake_dfs)

    assert result == {"Episodes": [1, 3, 5]}

    uasc_last = pd.DataFrame(
        [
            {"CHILD": "222", "DUC": "01/01/1990", "ETC": pd.NA},
            {"CHILD": "345", "DUC": pd.NA, "ETC": pd.NA},
        ]
    )

    fake_dfs = {"Episodes": fake_episodes, "UASC_last": uasc_last}

    result = validate(fake_dfs)

    assert result == {"Episodes": [3, 5]}
