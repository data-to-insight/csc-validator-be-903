import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="164",
    message="Distance is not valid. Please check a valid postcode has been entered. [NOTE: This check will result in false positives for children formerly UASC not identified as such in loaded data]",
    affected_fields=["PL_DISTANCE"],
)

# If not (<UASC> = '1' or <COLLECTION_YEAR> -1 <UASC> = '1' or <COLLECTION_YEAR> -2 <UASC> = '1') and if <LS> not = 'V3' or 'V4' then <PL_DISTANCE> must be between '0.0' and '999.9' Note: <PL_DISTANCE> is a calculated value based on Postcode.
def validate(dfs):
    # Headerlast also used if present
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]

        # Note the initial positions. Freeze a copy of the index values into a column
        epi["origidx"] = epi.index

        # Work out who is UASC or formerly UASC
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
            # drop all CHILD IDs that ever have UASC == 1
            epi = epi.merge(
                header[["CHILD"]], how="left", on="CHILD", indicator=True
            ).query('merge == "leftonly"')
        else:
            # if theres no UASC column in header, either from XML data, inferred for CSV in ingress, or added above
            # then we can't identify anyone as UASC/formerly UASC
            return {}
        # PLDISTANCE is added when the uploaded files are read into the tool. The code that does this is found in datastore.py
        epi = epi[epi["PLDISTANCE"].notna()]
        checkinrange = (epi["PLDISTANCE"].astype("float") < 0.0) | (
            epi["PLDISTANCE"].astype("float") > 999.9
        )
        errlist = epi.loc[(checkinrange), "origidx"].sortvalues().unique().tolist()

        return {"Episodes": errlist}


def test_validate():
    import pandas as pd

    fake_episodes = pd.DataFrame(
        [
            {"CHILD": "111", "LS": "V3", "PL_DISTANCE": "0.0"},  # 0 ignore: LS
            {"CHILD": "222", "LS": "V1", "PL_DISTANCE": pd.NA},  # 1
            {"CHILD": "222", "LS": "V5", "PL_DISTANCE": "-2"},  # 2 fail
            {"CHILD": "333", "LS": "V1", "PL_DISTANCE": "3.5"},  # 3 pass
            {"CHILD": "333", "LS": "V2", "PL_DISTANCE": "1000"},  # 4 fail
            {"CHILD": "345", "LS": "V7", "PL_DISTANCE": "1380"},  # 5 ignore: UASC
        ]
    )
    fake_header = pd.DataFrame(
        [
            {"CHILD": "111", "UASC": "0"},
            {"CHILD": "222", "UASC": "0"},
            {"CHILD": "333", "UASC": "0"},
            {"CHILD": "345", "UASC": "0"},
        ]
    )
    fake_header_last = pd.DataFrame(
        [
            {"CHILD": "111", "UASC": "0"},
            {"CHILD": "222", "UASC": "0"},
            {"CHILD": "333", "UASC": "0"},
            {"CHILD": "345", "UASC": "1"},
        ]
    )

    fake_dfs = {
        "Episodes": fake_episodes,
        "Header": fake_header,
        "Header_last": fake_header_last,
    }

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 4]}

    uasc_last = pd.DataFrame(
        [
            {"CHILD": "333", "DUC": "something"},  # [3] in episodes - passes now
            {"CHILD": "345", "DUC": pd.NA},  # [8] in episodes - still fails
        ]
    )

    dfs = {"Episodes": fake_episodes, "Header": fake_header, "UASC_last": uasc_last}
    result = error_func(dfs)
    assert result == {"Episodes": [2, 5]}
