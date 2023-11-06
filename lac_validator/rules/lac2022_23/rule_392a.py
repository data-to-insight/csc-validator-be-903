import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="392a",
    message="Child is looked after but no distance is recorded. [NOTE: This check may result in false positives for children formerly UASC]",
    affected_fields=["PL_DISTANCE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        # If <LS> not = 'V3' or 'V4' and <UASC> = '0' and <COLLECTION YEAR> - 1 <UASC> = '0' and <COLLECTION YEAR> - 2 <UASC> = '0' then <PL_DISTANCE> must be provided
        epi = dfs["Episodes"]
        epi["orig_idx"] = epi.index

        header = pd.DataFrame()
        if "Header" in dfs:
            header = pd.concat((header, dfs["Header"]), axis=0)
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
                header[["CHILD", "UASC"]], how="left", on="CHILD", indicator=True
            )
            epi = epi[epi["_merge"] == "left_only"]
        else:
            return {}

        # Check that the episodes LS are neither V3 or V4.
        epi = epi.query("(~LS.isin(['V3','V4'])) & ( PL_DISTANCE.isna())")
        err_list = epi["orig_idx"].tolist()
        err_list.sort()

        return {"Episodes": err_list}


def test_validate():
    import pandas as pd

    fake_episodes = pd.DataFrame(
        [
            {"CHILD": "111", "LS": "L1", "PL_DISTANCE": "XX1"},  # 0
            {"CHILD": "222", "LS": "L1", "PL_DISTANCE": pd.NA},  # 1 fail
            {"CHILD": "222", "LS": "V3", "PL_DISTANCE": "XX1"},  # 2
            {"CHILD": "333", "LS": "L1", "PL_DISTANCE": pd.NA},  # 3 fail
            {"CHILD": "333", "LS": "V4", "PL_DISTANCE": "XX1"},  # 4
            {"CHILD": "345", "LS": "L1", "PL_DISTANCE": pd.NA},  # 5 fail
            {"CHILD": "444", "LS": "L1", "PL_DISTANCE": "XX1"},  # 6
            {
                "CHILD": "444",
                "LS": "V3",
                "PL_DISTANCE": pd.NA,
            },  # 7 pass since LS isin [V3, V4]
            {"CHILD": "555", "LS": "L1", "PL_DISTANCE": pd.NA},  # 8 fail
        ]
    )
    fake_header = pd.DataFrame(
        [
            {"CHILD": "111", "UASC": "1"},  # 0
            {"CHILD": "222", "UASC": "0"},  # 2
            {"CHILD": "333", "UASC": "0"},  # 4
            {"CHILD": "345", "UASC": "0"},  # 5
            {"CHILD": "444", "UASC": "0"},  # 6
            {"CHILD": "555", "UASC": "0"},  # 6
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

    dfs = {
        "Episodes": fake_episodes,
        "Header": fake_header,
        "Header_last": fake_header_last,
    }
    result = validate(dfs)
    assert result == {"Episodes": [1, 3, 5, 8]}

    uasc_last = pd.DataFrame(
        [
            {"CHILD": "333", "DUC": "something"},  # [3] in episodes - passes now
            {"CHILD": "555", "DUC": pd.NA},  # [8] in episodes - still fails
        ]
    )

    dfs = {"Episodes": fake_episodes, "Header": fake_header, "UASC_last": uasc_last}
    result = validate(dfs)
    assert result == {"Episodes": [1, 5, 8]}
