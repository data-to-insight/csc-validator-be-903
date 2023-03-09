import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="406",
        description="Child is Unaccompanied Asylum-Seeking Child (UASC) or was formerly UASC. Distance should be "
        "blank. [NOTE: This check will result in false negatives for children formerly UASC not "
        "identified as such in loaded data]",
        affected_fields=["PL_DISTANCE"],
    )

    # If <UASC> = '1' or <COLLECTION YEAR> - 1 <UASC> = '1' or <COLLECTION YEAR> - 2 <UASC> = '1' Then
    # <PL_DISTANCE> should not be provided Note: <PL_DISTANCE> is a derived field in most instances
    def _validate(dfs):
        # Header_last also used if present
        if "Episodes" not in dfs:
            return {}
        else:
            epi = dfs["Episodes"]

            # Note the initial positions. Freeze a copy of the index values into a column
            epi["orig_idx"] = epi.index

            # Work out who is formerly
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
                epi = epi.merge(header[["CHILD"]], how="inner", on="CHILD")
            else:
                # if theres no UASC column in header, either from XML data, inferred for CSV in ingress, or added above
                # then we can't identify anyone as UASC/formerly UASC
                return {}
            # PL_DISTANCE is added when the uploaded files are read into the tool. The code that does this is found in datastore.py

            err_list = (
                epi.loc[epi["PL_DISTANCE"].notna(), "orig_idx"]
                .sort_values()
                .unique()
                .tolist()
            )

            return {"Episodes": err_list}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_episodes = pd.DataFrame(
        [
            {"CHILD": "111", "PL_DISTANCE": "XX1"},  # 0 fail
            {"CHILD": "222", "PL_DISTANCE": pd.NA},  # 1
            {"CHILD": "222", "PL_DISTANCE": "XX1"},  # 2 fail
            {"CHILD": "333", "PL_DISTANCE": pd.NA},  # 3
            {
                "CHILD": "333",
                "PL_DISTANCE": "XX1",
            },  # 4 ignore: it is not present in any uasc table.
            {"CHILD": "345", "PL_DISTANCE": pd.NA},  # 5
            {"CHILD": "444", "PL_DISTANCE": "XX1"},  # 6 fail
            {"CHILD": "444", "PL_DISTANCE": pd.NA},  # 7
        ]
    )
    fake_header = pd.DataFrame(
        [
            {"CHILD": "111", "UASC": "1"},  # 0
            {"CHILD": "222", "UASC": "0"},  # 2
            {"CHILD": "333", "UASC": "0"},  # 4
            {"CHILD": "345", "UASC": "1"},  # 5
            {"CHILD": "444", "UASC": "0"},  # 6
        ]
    )
    fake_header_last = pd.DataFrame(
        [
            {"CHILD": "111", "UASC": "0"},  # 0
            {"CHILD": "222", "UASC": "1"},  # 2
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

    assert result == {"Episodes": [0, 2, 6]}
