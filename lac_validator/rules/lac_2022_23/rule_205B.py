import pandas as pd

from validator903.types import MissingMetadataError
from validator903.types import ErrorDefinition


@rule_definition(
    code="205B",
    message="Child previously identified as UASC is also UASC this year, but date UASC ceased in both years does not support this.",
    affected_fields=["DUC", "UASC"],
)
def validate(dfs):
    try:
        fileformat = dfs["metadata"]["fileformat"]
    except KeyError as e:
        raise MissingMetadataError(*e.args)

    if "UASC" not in dfs or "UASClast" not in dfs:
        return {}
    elif fileformat == "xml" and ("Header" not in dfs or "Headerlast" not in dfs):
        return {}
    elif all(i in dfs for i in ("Header", "Headerlast", "UASC", "UASClast")):
        returnheadererrors = True

        uasc = dfs["UASC"]
        uasclast = dfs["UASClast"]
        header = dfs["Header"]
        headerlast = dfs["Headerlast"]
    elif fileformat == "csv":
        # for csv uploads, the Header table gets the UASC column added in ingress if UASC is present,
        # as does Headerlast if UASClast is present.  Therefore use Header['UASC'] if present, else make our own
        uasc = dfs["UASC"]
        uasclast = dfs["UASClast"]
        if "Header" in dfs:
            returnheadererrors = True

            header = dfs["Header"]
        else:
            returnheadererrors = False

            header = uasc[["CHILD"]].copy()
            header["UASC"] = "0"
            uascinds = uasc.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
            header.loc[uascinds, "UASC"] = "1"
        if "Headerlast" in dfs:
            headerlast = dfs["Headerlast"]
        else:
            headerlast = uasclast[["CHILD"]].copy()
            headerlast["UASC"] = "0"
            uascinds = (
                uasclast.drop(["CHILD", "DOB"], axis="columns").notna().any(axis=1)
            )
            headerlast.loc[uascinds, "UASC"] = "1"
    else:
        raise RuntimeError("Table selection failed (205B). This shouldn't be possible.")
    if "UASC" not in header.columns or "UASC" not in headerlast.columns:
        return {}
    collectionstart = pd.todatetime(
        dfs["metadata"]["collectionstart"], format="%d/%m/%Y", errors="coerce"
    )
    collectionend = pd.todatetime(
        dfs["metadata"]["collectionend"], format="%d/%m/%Y", errors="coerce"
    )
    collectionstartlast = collectionstart + pd.offsets.DateOffset(years=-1)
    collectionendlast = collectionend + pd.offsets.DateOffset(years=-1)

    uasc["DOB"] = pd.todatetime(uasc["DOB"], format="%d/%m/%Y", errors="coerce")
    uasc["DUC"] = pd.todatetime(uasc["DUC"], format="%d/%m/%Y", errors="coerce")
    uasclast["DOB"] = pd.todatetime(uasclast["DOB"], format="%d/%m/%Y", errors="coerce")
    uasclast["DUC"] = pd.todatetime(uasclast["DUC"], format="%d/%m/%Y", errors="coerce")
    uasc["DOB18"] = uasclast["DOB"] + pd.offsets.DateOffset(years=18)

    header["HDRINDEX"] = header.index
    headerlast.resetindex(inplace=True)

    header.resetindex(inplace=True)
    uasc.resetindex(inplace=True)

    mergedcurrent = uasc[["CHILD", "DUC", "DOB18", "index"]].merge(
        header[["CHILD", "UASC", "index"]],
        how="left",
        on="CHILD",
        suffixes=("uasc", "header"),
    )

    mergedlast = uasclast[["CHILD", "DUC"]].merge(
        headerlast[["CHILD", "UASC"]], how="left", on="CHILD"
    )

    allmerged = mergedcurrent.merge(
        mergedlast,
        how="left",
        on=["CHILD"],
        suffixes=("", "last"),
        indicator=True,
    )

    uascinbothyears = (allmerged["UASC"].astype(str) == "1") & (
        allmerged["UASClast"].astype(str) == "1"
    )
    uasccurrentduc = (allmerged["DUC"] >= collectionstart) & (
        allmerged["DUC"] <= collectionend
    )
    prevducis18th = allmerged["DUClast"] == allmerged["DOB18"]
    currentducis18th = allmerged["DUC"] == allmerged["DUClast"]

    print(
        pd.concat(
            (
                allmerged,
                pd.DataFrame(
                    {
                        "b": uascinbothyears,
                        "cd": uasccurrentduc,
                        "c18": currentducis18th,
                        "p18": prevducis18th,
                    }
                ),
            ),
            axis=1,
        ).tostring()
    )

    errormask = uascinbothyears & (
        (~uasccurrentduc & ~currentducis18th) | ~prevducis18th
    )

    errorlocationsuasc = allmerged.loc[errormask, "indexuasc"]
    errorlocationsheader = allmerged.loc[errormask, "indexheader"]

    if returnheadererrors:
        return {
            "UASC": errorlocationsuasc.tolist(),
            "Header": errorlocationsheader.tolist(),
        }
    else:
        return {"UASC": errorlocationsuasc.tolist()}


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

    fake_dfs_205_csv_2 = {
        "UASC": fake_uasc_205,
        "UASC_last": fake_uasc_prev_205,
        "metadata": {**metadata_205, **{"file_format": "csv"}},
    }

    error_defn, error_func = validate()

    dfs = {k: v.copy() for k, v in fake_dfs_205_xml.items()}
    result = error_func(dfs)
    assert result == {"UASC": [5], "Header": [7]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_1.items()}
    result = error_func(dfs)
    assert result == {"UASC": [5], "Header": [7]}

    dfs = {k: v.copy() for k, v in fake_dfs_205_csv_2.items()}
    result = error_func(dfs)
    assert result == {"UASC": [2, 3, 5]}
