import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="392B",
    message="Child is looked after but no postcodes are recorded. [NOTE: This check may result in false "
    "positives for children formerly UASC, particularly if current & prior year UASC data not loaded]",
    affected_fields=["HOME_POST", "PL_POST"],
)
def validate(dfs):
    # Will also use Header/UASC and/or Headerlast/UASClast for former UASC status
    if "Episodes" not in dfs:
        return {}
    else:
        # If <LS> not = 'V3' or 'V4' and <UASC> = '0' and <COLLECTION YEAR> - 1 <UASC> = '0' and <COLLECTION YEAR> - 2 <UASC> = '0' then <HOMEPOST> and <PLPOST> should be provided.
        epi = dfs["Episodes"]
        epi["originalindex"] = epi.index

        # Remove any children with evidence of former UASC status
        header = pd.DataFrame()
        if "Header" in dfs:
            headercurrent = dfs["Header"]
            header = pd.concat((header, headercurrent), axis=0)
        elif "UASC" in dfs:
            uasc = dfs["UASC"]
            uasc = uasc.loc[
                uasc.drop("CHILD", axis="columns").notna().any(axis=1), ["CHILD"]
            ].copy()
            uasc.loc[:, "UASC"] = "1"
            header = pd.concat((header, uasc), axis=0)

        if "Headerlast" in dfs:
            header = pd.concat((header, dfs["Headerlast"]), axis=0)
        elif "UASClast" in dfs:
            uasc = dfs["UASClast"]
            uasc = uasc.loc[
                uasc.drop("CHILD", axis="columns").notna().any(axis=1), ["CHILD"]
            ].copy()
            uasc.loc[:, "UASC"] = "1"
            header = pd.concat((header, uasc), axis=0)

        if "UASC" in header.columns:
            header = header[header.UASC == "1"].dropduplicates("CHILD")
            epi = epi.merge(
                header[["CHILD"]], how="left", on="CHILD", indicator=True
            ).query("merge == 'leftonly'")

        # Remove episodes where LS is V3/V4
        epi = epi.query("(~LS.isin(['V3','V4']))")

        # Remove episodes with postcodes filled in
        epi = epi.query("(HOMEPOST.isna() | PLPOST.isna())")

        # Get error indices
        errlist = epi["originalindex"].sortvalues().tolist()

        return {"Episodes": errlist}


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

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 3, 5]}

    uasc_last = pd.DataFrame(
        [
            {"CHILD": "222", "DUC": "01/01/1990", "ETC": pd.NA},
            {"CHILD": "345", "DUC": pd.NA, "ETC": pd.NA},
        ]
    )

    fake_dfs = {"Episodes": fake_episodes, "UASC_last": uasc_last}

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 5]}
