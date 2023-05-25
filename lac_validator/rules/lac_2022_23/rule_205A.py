import pandas as pd

from validator903.types import MissingMetadataError
from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="205A",
    message="Child identified as UASC last year is no longer UASC this year, but date UASC ceased in both "
    "years does not support this.",
    affected_fields=["CHILD", "UASC"],
)
def validate(dfs):
    try:
        file_format = dfs["metadata"]["file_format"]
    except KeyError as e:
        raise MissingMetadataError(*e.args)

    if "UASC" not in dfs or "UASC_last" not in dfs:
        return {}
    elif file_format == "xml" and ("Header" not in dfs or "Header_last" not in dfs):
        return {}
    elif all(i in dfs for i in ("Header", "Header_last", "UASC", "UASC_last")):
        return_header_errors = True

        uasc = dfs["UASC"]
        uasc_last = dfs["UASC_last"]
        header = dfs["Header"]
        header_last = dfs["Header_last"]
    elif file_format == "csv":
        # for csv uploads, the Header table gets the UASC column added in ingress if UASC is present,
        # as does Header_last if UASC_last is present.  Therefore use Header['UASC'] if present, else make our own
        uasc = dfs["UASC"]
        uasc_last = dfs["UASC_last"]
        if "Header" in dfs:
            return_header_errors = True

            header = dfs["Header"]
        else:
            return_header_errors = False

            header = uasc[["CHILD"]].copy()
            header["UASC"] = "0"
            uasc_inds = uasc.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
            header.loc[uasc_inds, "UASC"] = "1"
        if "Header_last" in dfs:
            header_last = dfs["Header_last"]
        else:
            header_last = uasc_last[["CHILD"]].copy()
            header_last["UASC"] = "0"
            uasc_inds = (
                uasc_last.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
            )
            header_last.loc[uasc_inds, "UASC"] = "1"
    else:
        raise RuntimeError("Table selection failed (205C). This shouldn't be possible.")
    if "UASC" not in header.columns or "UASC" not in header_last.columns:
        return {}

    collection_start = pd.to_datetime(
        dfs["metadata"]["collection_start"], format="%d/%m/%Y", errors="coerce"
    )
    collection_end = pd.to_datetime(
        dfs["metadata"]["collection_end"], format="%d/%m/%Y", errors="coerce"
    )
    collection_start_last = collection_start + pd.offsets.DateOffset(years=-1)
    collection_end_last = collection_end + pd.offsets.DateOffset(years=-1)

    uasc_last["DUC"] = pd.to_datetime(
        uasc_last["DUC"], format="%d/%m/%Y", errors="coerce"
    )

    header.reset_index(inplace=True)
    uasc.reset_index(inplace=True)

    merged_current = uasc[["CHILD", "DUC", "index"]].merge(
        header[["CHILD", "UASC", "index"]],
        how="left",
        on="CHILD",
        suffixes=("_uasc", "_header"),
    )

    merged_last = uasc_last[["CHILD", "DUC"]].merge(
        header_last[["CHILD", "UASC"]], how="left", on="CHILD"
    )

    all_merged = merged_current.merge(
        merged_last,
        how="left",
        on=["CHILD"],
        suffixes=("", "_last"),
        indicator=True,
    )

    last_year_only = (all_merged["UASC"].astype(str) != "1") & (
        all_merged["UASC_last"].astype(str) == "1"
    )
    duc_last_in_prev_year = (all_merged["DUC_last"] >= collection_start_last) & (
        all_merged["DUC_last"] <= collection_end_last
    )
    uasc_current_duc = all_merged["DUC"].notna()

    error_mask = last_year_only & (uasc_current_duc | ~duc_last_in_prev_year)

    error_locations_uasc = (
        all_merged.loc[error_mask, "index_uasc"].dropna().astype(int).sort_values()
    )
    error_locations_header = (
        all_merged.loc[error_mask, "index_header"].dropna().astype(int).sort_values()
    )
    if return_header_errors:
        return {
            "UASC": error_locations_uasc.to_list(),
            "Header": error_locations_header.to_list(),
        }
    else:
        return {"UASC": error_locations_uasc.to_list()}


def test_validate():
    import pandas as pd

    fake_uasc_205 = pd.DataFrame(
        [
            {"CHILD": "101", "DOB": "28/10/2004", "DUC": pd.NA},  # Pass C
            {"CHILD": "102", "DOB": "04/06/2004", "DUC": pd.NA},  # Pass A
            {"CHILD": "103", "DOB": "03/03/2002", "DUC": "10/07/2020"},  # Fail A
            {"CHILD": "104", "DOB": "28/03/2003", "DUC": "14/05/2021"},  # Fail A
            {"CHILD": "105", "DOB": "16/04/2001", "DUC": "16/04/2019"},  # Fail B
            {"CHILD": "106", "DOB": "04/11/2004", "DUC": "16/06/2021"},  # Fail B
            {"CHILD": "107", "DOB": "23/07/2002", "DUC": "23/07/2020"},  # Pass B
            {"CHILD": "108", "DOB": "19/02/2003", "DUC": pd.NA},  # Fail C
            {"CHILD": "109", "DOB": "14/06/2003", "DUC": "14/06/2021"},  # Fail D
            {"CHILD": "110", "DOB": "14/06/2003", "DUC": pd.NA},  # Fail D
        ]
    )

    fake_uasc_prev_205 = pd.DataFrame(
        [
            {"CHILD": "101", "DOB": "28/10/2004", "DUC": pd.NA},  # Pass C
            {"CHILD": "102", "DOB": "04/06/2004", "DUC": "20/01/2020"},  # Pass A
            {"CHILD": "103", "DOB": "03/03/2002", "DUC": "10/07/2020"},  # Fail A
            {"CHILD": "104", "DOB": "28/03/2003", "DUC": "14/05/2021"},  # Fail A
            {"CHILD": "105", "DOB": "16/04/2001", "DUC": "16/04/2019"},  # Fail B
            {"CHILD": "106", "DOB": "04/11/2004", "DUC": "04/11/2023"},  # Fail B
            {"CHILD": "107", "DOB": "23/07/2002", "DUC": "23/07/2020"},  # Pass B
            {"CHILD": "108", "DOB": "19/02/2003", "DUC": "19/02/2021"},  # Fail C
            {"CHILD": "109", "DOB": "14/06/2003", "DUC": "14/06/2021"},  # Fail D
            {"CHILD": "110", "DOB": "14/06/2003", "DUC": "14/06/2021"},  # Fail D
        ]
    )

    fake_header_205 = pd.DataFrame(
        [
            {"CHILD": "101", "DOB": "28/10/2004", "UASC": "0"},  # Pass C
            {"CHILD": "108", "DOB": "19/02/2003", "UASC": "0"},  # Fail C
            {"CHILD": "109", "DOB": "14/06/2003", "UASC": "1"},  # Fail D
            {"CHILD": "102", "DOB": "04/06/2004", "UASC": "0"},  # Pass A
            {"CHILD": "103", "DOB": "03/03/2002", "UASC": "0"},  # Fail A
            {"CHILD": "104", "DOB": "28/03/2003", "UASC": "0"},  # Fail A
            {"CHILD": "105", "DOB": "16/04/2001", "UASC": "1"},  # Fail B
            {"CHILD": "106", "DOB": "04/11/2004", "UASC": "1"},  # Fail B
            {"CHILD": "107", "DOB": "23/07/2002", "UASC": "1"},  # Pass B
            {"CHILD": "110", "DOB": "03/03/2002", "UASC": "0"},
        ]
    )

    prev_fake_header_205 = pd.DataFrame(
        [
            {"CHILD": "102", "DOB": "04/06/2004", "UASC": "1"},  # Pass A
            {"CHILD": "103", "DOB": "03/03/2002", "UASC": "1"},  # Fail A
            {"CHILD": "104", "DOB": "28/03/2003", "UASC": "1"},  # Fail A
            {"CHILD": "101", "DOB": "28/10/2004", "UASC": "0"},  # Pass C
            {"CHILD": "105", "DOB": "16/04/2001", "UASC": "1"},  # Fail B
            {"CHILD": "106", "DOB": "04/11/2004", "UASC": "1"},  # Fail B
            {"CHILD": "107", "DOB": "23/07/2002", "UASC": "1"},  # Pass B
            {"CHILD": "108", "DOB": "19/02/2003", "UASC": "0"},  # Fail C
            {"CHILD": "109", "DOB": "14/06/2003", "UASC": "0"},  # Fail D
            {"CHILD": "110", "DOB": "03/03/2002", "UASC": "0"},
        ]
    )

    metadata_205 = {
        "collection_start": "01/04/2020",
        "collection_end": "31/03/2021",
    }

    fake_dfs_205_xml = {
        "UASC": fake_uasc_205,
        "UASC_last": fake_uasc_prev_205,
        "Header": fake_header_205,
        "Header_last": prev_fake_header_205,
        "metadata": {**metadata_205, **{"file_format": "xml"}},
    }

    fake_dfs_205_csv_1 = {
        "UASC": fake_uasc_205,
        "UASC_last": fake_uasc_prev_205,
        "Header": fake_header_205,
        "metadata": {**metadata_205, **{"file_format": "csv"}},
    }

    

    dfs = {k: v.copy() for k, v in fake_dfs_205_xml.items()}
    result = error_func(dfs)
    assert result == {"UASC": [2, 3], "Header": [4, 5]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_1.items()}
    result = error_func(dfs)
    assert result == {"UASC": [2, 3, 7, 9], "Header": [1, 4, 5, 9]}
