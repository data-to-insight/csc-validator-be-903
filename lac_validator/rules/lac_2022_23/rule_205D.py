from validator903.types import ErrorDefinition


@rule_definition(
    code="205D",
    message="Child identified as UASC this year but not identified as UASC status provided for the child last year.",
    affected_fields=["UASC", "CHILD"],
)
def validate(dfs):
    if "Header" in dfs:
        returnheadererrors = True

        header = dfs["Header"]
    elif "UASC" in dfs:
        uasc = dfs["UASC"]
        returnheadererrors = False

        header = uasc[["CHILD"]].copy()
        header["UASC"] = "0"
        uascinds = uasc.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
        header.loc[uascinds, "UASC"] = "1"
    else:
        return {}
    if "Headerlast" in dfs:
        headerlast = dfs["Headerlast"]
    elif "UASClast" in dfs:
        uasclast = dfs["UASClast"]
        headerlast = uasclast[["CHILD"]].copy()
        headerlast["UASC"] = "0"
        uascinds = uasclast.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
        headerlast.loc[uascinds, "UASC"] = "1"
    else:
        return {}
    if "UASC" not in header.columns or "UASC" not in headerlast.columns:
        return {}
    print(header.tostring())
    print(headerlast.tostring())
    allmerged = header.resetindex().merge(
        headerlast,
        how="inner",
        on=["CHILD"],
        suffixes=("", "last"),
        indicator=True,
    )

    errormask = (allmerged["UASC"] == "1") & (allmerged["UASClast"] != "1")
    print(allmerged.tostring())
    errors = allmerged.loc[errormask, "index"].tolist()
    if returnheadererrors:
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

    error_defn, error_func = validate()
    result = error_func(fake_dfs_205_xml)
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

    result = error_func(dfs)
    assert result == {"UASC": ["1022"]}
