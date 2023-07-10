import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="205D",
    message="Child identified as UASC this year but not identified as UASC status provided for the child last year.",
    affected_fields=["UASC", "CHILD"],
)
def validate(dfs):
    if "Header" in dfs:
        return_header_errors = True

        header = dfs["Header"]
    elif "UASC" in dfs:
        uasc = dfs["UASC"]
        return_header_errors = False

        header = uasc[["CHILD"]].copy()
        header["UASC"] = "0"
        uasc_inds = uasc.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
        header.loc[uasc_inds, "UASC"] = "1"
    else:
        return {}
    if "Header_last" in dfs:
        header_last = dfs["Header_last"]
    elif "UASC_last" in dfs:
        uasc_last = dfs["UASC_last"]
        header_last = uasc_last[["CHILD"]].copy()
        header_last["UASC"] = "0"
        uasc_inds = uasc_last.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
        header_last.loc[uasc_inds, "UASC"] = "1"
    else:
        return {}
    if "UASC" not in header.columns or "UASC" not in header_last.columns:
        return {}
    all_merged = header.reset_index().merge(
        header_last,
        how="inner",
        on=["CHILD"],
        suffixes=("", "_last"),
        indicator=True,
    )

    error_mask = (all_merged["UASC"] == "1") & (all_merged["UASC_last"] != "1")
    errors = all_merged.loc[error_mask, "index"].to_list()
    if return_header_errors:
        return {"Header": errors}
    else:
        return {"UASC": errors}


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

    fake_dfs_205_csv_2 = {
        "UASC": fake_uasc_205,
        "UASC_last": fake_uasc_prev_205,
        "metadata": {**metadata_205, **{"file_format": "csv"}},
    }

    result = validate(fake_dfs_205_xml)
    assert result == {"Header": [2]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_2.items()}
    dfs["UASC_last"].loc["1001"] = {
        "CHILD": "1001",
        "DOB": "23/07/2002",
        "DUC": "01/01/2020",
    }
    dfs["UASC"].loc["1001"] = {
        "CHILD": "1001",
        "DOB": "23/07/2002",
        "DUC": "99/bad/date",
    }
    dfs["UASC"].loc["1022"] = {
        "CHILD": "1022",
        "DOB": "23/07/2002",
        "DUC": "01/01/2020",
    }
    dfs["UASC_last"].loc["1022"] = {"CHILD": "1022", "DOB": "23/07/2002", "DUC": pd.NA}

    result = validate(dfs)
    assert result == {"UASC": ["1022"]}
