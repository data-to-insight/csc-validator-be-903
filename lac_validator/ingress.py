import collections.abc
import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from time import perf_counter as now
from typing import Dict, Iterator, List, Tuple, Union

import pandas as pd
from numpy import nan
from pandas import DataFrame

from lac_validator.config import column_names
from lac_validator.datastore import la_df, merge_postcodes
from lac_validator.types import UploadedFile, UploadError

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # uncomment if you want to see debug messages


class Timer:
    def __init__(self):
        self._prev = None
        self._zero = None
        self.t0

    @property
    def t0(self):
        self._zero = now()
        self._prev = self._zero
        return f"Starting timer"

    @property
    def t(self):
        t = now()
        elapsed = t - self._prev
        self._prev = t
        return f"{elapsed:05.2f}s (total {t - self._zero:05.02f}s)"


sc = Timer()


class _BufferedUploadedFile(collections.abc.Mapping):
    def __init__(self, file, name, description):
        self.name = name
        self.description = description
        self.file = Path(file)
        if not self.file.is_file():
            raise FileNotFoundError(f"{self.file} not found.")

    def __getitem__(self, k):
        if k == "name":
            return self.name
        elif k == "description":
            return self.description
        elif k == "file_content":
            with open(self.file, "rb") as file:
                return file.read()
        else:
            raise AttributeError(f"{k} not found")

    def __len__(self) -> int:
        return 3

    def __iter__(self) -> Iterator:
        pass


def read_from_text(
    raw_files: List[UploadedFile],
) -> Tuple[Dict[str, DataFrame], Dict[str, Union[str, DataFrame]]]:
    """
    Reads from a raw list of files passed from javascript. These files are of
    the form e.g.
    [
        {name: 'filename.csv', file_content: <file contents>, description: <upload metadata>}
    ]

    This function will try to catch most basic upload errors, and dispatch other errors
    to either the csv or xml reader based on the file extension.
    """
    logger.info(f"Reading from text. {sc.t0}")
    metadata_extras = {}

    CH_uploaded = [f for f in raw_files if f["description"] == "CH lookup"]
    SCP_uploaded = [f for f in raw_files if f["description"] == "SCP lookup"]
    num_of_CH_and_SCP = (len(CH_uploaded), len(SCP_uploaded))

    logger.info(f"#CH: {num_of_CH_and_SCP[0]}, #SCP:{num_of_CH_and_SCP[1]}")

    if max(num_of_CH_and_SCP) > 1:
        raise UploadError(
            f"{num_of_CH_and_SCP[0]} (Children's Homes List) and {num_of_CH_and_SCP[1]} (Social Care Providers List) "
            f"URN lookup tables were loaded - Please only load a single file in each box."
        )
    elif set(num_of_CH_and_SCP) == {0, 1}:
        if CH_uploaded:
            # Checks if a single CH list has wrongly been uploaded, or if a single combined SCPCH list has been uploaded
            combined_scpch = combined_ch_scp_check(CH_uploaded[0])
            if combined_scpch:
                logger.info(
                    f"Combined 'Childrens home' and 'Social Care Providers' lists detected. {sc.t}"
                )
                provider_info_df = scpch_provider_info_table(scpch=CH_uploaded[0])
                metadata_extras["provider_info"] = provider_info_df
            else:
                raise UploadError(
                    "Please load both the latest 'Children's Homes' and 'Social Care Providers' lists "
                    "from Ofsted into their respective boxes above."
                )
        else:
            raise UploadError(
                "Please load both the latest 'Children's Homes' and 'Social Care Providers' lists "
                "from Ofsted into their respective boxes above."
            )
    elif set(num_of_CH_and_SCP) == {1}:
        logger.info(
            f"Ofsted CH & SCP spreadsheets received - constructing provider info table. {sc.t}"
        )
        (CH_uploaded,) = CH_uploaded  # These should both be single-element lists
        (SCP_uploaded,) = SCP_uploaded
        provider_info_df = construct_provider_info_table(
            CH=CH_uploaded, SCP=SCP_uploaded
        )
        metadata_extras["provider_info"] = provider_info_df

        # logger.info(
        #     "created providers table. shape:{1} rows, {0}".format(
        #         *provider_info_df.shape
        #     )
        # )
        logger.debug(f'{", ".join(provider_info_df.columns)}')
        logger.debug(f"providers dtypes: {provider_info_df.dtypes}")

    else:
        logger.info(
            "Ofsted CH & SCP spreadsheets not loaded - checks involving URN lookup will be skipped."
        )

    raw_files = [
        f for f in raw_files if f["description"] not in ("CH lookup", "SCP lookup")
    ]

    extensions = list(set([f["name"].split(".")[-1].lower() for f in raw_files]))

    if len(raw_files) == 0:
        raise UploadError("No SSDA 903 files uploaded!")
    elif len(extensions) > 1:
        raise UploadError(
            f"Mix of CSV and XML files found ({extensions})! Please reupload."
        )
    else:
        if extensions == ["csv"]:
            metadata_extras["file_format"] = "csv"
            return read_csvs_from_text(raw_files), metadata_extras
        elif extensions == ["xml"]:
            metadata_extras["file_format"] = "xml"
            return read_xml_from_text(raw_files[0]["file_content"]), metadata_extras
        else:
            raise UploadError(f"Unknown file type {extensions[0]} found.")


def construct_provider_info_table(CH: UploadedFile, SCP: UploadedFile):
    """
    inputs:
    CH (childrens homes) and SCP (social care providers) are either strings containing a path to
    the excel files, or the files' contents as passed in by the frontend

    returns:
    provider_info_df is a dataframe
    (*) it will be stored in dfs['metadata']['provider_info'] if it has been uploaded
    (*) if it's not there, then  return {} for rules requiring it
    (*) the columns will be ['URN', 'PLACE_CODES', 'PROVIDER_CODES', 'REG_END', 'POSTCODE', 'LA_CODE']:
    (*) all cols will be strings (object dtype) except REG_END which will be datetime
        - URN:
            merge on this.
        - PLACE_CODES and PROVIDER_CODES:
            strings of codes separated by commas: ['PR4', 'PR1,PR2', etc..]
        - REG_END:
            date provider should have closed (usually blank) - note its type will already be datetime64
        - POSTCODE:
            postcode - upper-cased, spaces removed
        - LA_CODE_INFERRED and LA_NAME_INFERRED:
            utla code and utla name - obtained from la_df by matching on provider postcode
            (!) These may differ from the LA named in the files, either due to formatting, or if they serve
            different LA to where they are located. Rule descriptions should mention this caveat.
        - LA_NAME_FROM_FILE
            LA name from uploaded files.
    """
    if not isinstance(CH, str):
        if not isinstance(CH["file_content"], bytes):
            CH_bytes = CH["file_content"].tobytes()
        else:
            CH_bytes = CH["file_content"]
    else:
        CH_bytes = CH
    if not isinstance(SCP, str):
        if not isinstance(SCP["file_content"], bytes):
            SCP_bytes = SCP["file_content"].tobytes()
        else:
            SCP_bytes = SCP["file_content"]
    else:
        SCP_bytes = SCP
    provider_info_cols = [
        "URN",
        "LA_NAME_FROM_FILE",
        "PLACE_CODES",
        "PROVIDER_CODES",
        "REG_END",
        "POSTCODE",
    ]
    logger.info(f"URN lookup bytes recieved. Reading excel files... {sc.t}")

    # read childrens homes file
    CH_sheets = pd.ExcelFile(CH_bytes, engine="openpyxl").sheet_names
    CH_cols = [
        "URN",
        "Local Authority",
        "Provider Code",
        "Provider Placement Code",
        "Closed Date",
        "Setting Postcode",
    ]

    # check whether file includes consolidated provider information sheet
    if "Provider information" in CH_sheets:
        CH_providers = pd.read_excel(
            CH_bytes, sheet_name="Provider information", engine="openpyxl"
        )
        logger.debug(
            f"Reading CH provider info from excel done. cols:{CH_providers.columns} {sc.t}"
        )

        try:
            CH_address = CH_providers[["URN", "Setting Postcode"]]
        except KeyError:
            try:
                CH_address = CH_providers[["URN"]]
                CH_providers = CH_providers.rename(
                    columns={"Setting Address Postcode": "Setting Postcode"}
                )
            except KeyError:
                raise print(
                    "Failed to find postcode column in Childrens Homes list "
                    '"Provider information" sheet. Expected "Setting Postcode"'
                )
        try:
            CH_providers = CH_providers[CH_cols[:]]
        except KeyError:
            raise UploadError(
                f'Failed to find required columns in Childrens Homes list "Provider information"'
                f' sheet. Expected: {", ".join(CH_cols[:])}'
            )
        CH_df = CH_providers
        del CH_providers, CH_address

    # if not check whether file includes separate setting and address sheets
    elif "Settings and Inspection Info" in CH_sheets and "Address Details" in CH_sheets:
        # this sheet contains all columns except the postcode
        CH_setting = pd.read_excel(
            CH_bytes, sheet_name="Settings and Inspection Info", engine="openpyxl"
        )
        logger.debug(
            f"Reading CH setting info from excel done. cols:{CH_setting.columns} {sc.t}"
        )
        # from this sheet we need only the postcode
        CH_address = pd.read_excel(
            CH_bytes, sheet_name="Address Details", engine="openpyxl"
        )
        logger.debug(
            f"Reading CH address info from excel done. cols:{CH_address.columns} {sc.t}"
        )

        try:
            CH_address = CH_address[["URN", "Setting Postcode"]]
        except KeyError:
            try:
                CH_address = CH_address[["URN", "Setting Address Postcode"]].rename(
                    columns={"Setting Address Postcode": "Setting Postcode"}
                )
            except KeyError:
                raise UploadError(
                    "Failed to find postcode column in Childrens Homes list "
                    '"Address Details" sheet. Expected "Setting Postcode"'
                )
        try:
            CH_setting = CH_setting[CH_cols[:-1]]
        except KeyError:
            raise UploadError(
                f'Failed to find required columns in Childrens Homes list "Setting and Inspection Info"'
                f' sheet. Expected: {", ".join(CH_cols[: -1])}'
            )

        # combine the postcode with the rest of the columns
        CH_df = pd.merge(left=CH_setting, right=CH_address, on="URN", how="inner")
        del CH_setting, CH_address

    else:
        raise UploadError(
            "Failed to find expected sheet names in Childrens Homes List. "
            'Expected "Provider information" or "Setting and Inspection Info" and "Address Details"'
        )

    CH_df["source"] = "CH List"
    CH_df["Provider Placement Code"] = CH_df["Provider Placement Code"].str.replace(
        "/", ","
    )
    provider_info_df = CH_df.rename(columns=dict(zip(CH_cols, provider_info_cols)))
    del CH_df
    logger.info(f"CH dataframe complete. Creating SCP dataframe {sc.t}")

    # read social care providers file
    SCP_current = pd.read_excel(
        SCP_bytes, engine="openpyxl", sheet_name=0
    )  # current providers
    logger.debug(
        f"Reading SCP_current from excel done. cols: {SCP_current.columns}. {sc.t}"
    )
    SCP_closed = pd.read_excel(
        SCP_bytes, engine="openpyxl", sheet_name=1
    )  # closed providers
    logger.debug(
        f"Reading SCP_closed from excel done. cols: {SCP_closed.columns}. {sc.t}"
    )

    SCP_cols = [
        "URN",
        "Local authority",
        "Placement code",
        "Placement provider code",
        "Deregistration date",
        "Setting postcode",
    ]
    try:
        SCP_current = SCP_current[[_ for _ in SCP_cols if _ != "Deregistration date"]]
    except KeyError:
        missing_cols = set(_ for _ in SCP_cols if _ != "Deregistration date") - set(
            SCP_current.columns
        )
        raise UploadError(
            f'Failed to find required columns in Social Care Providers list "Current providers"'
            f' sheet. Didnt find: {", ".join(missing_cols)}'
        )
    try:
        SCP_closed = SCP_closed[SCP_cols]
    except KeyError:
        missing_cols = set(SCP_cols) - set(SCP_closed.columns)
        raise UploadError(
            f'Failed to find required columns in Social Care Providers list "Providers closed"'
            f' sheet. Didnt find: {", ".join(missing_cols)}'
        )

    # concatenate the two SCP sheets and rename the columns
    SCP_df = pd.concat((SCP_current, SCP_closed)).rename(
        columns=dict(zip(SCP_cols, provider_info_cols))
    )
    SCP_df = SCP_df[SCP_df["URN"].notnull()]
    SCP_df["source"] = "SCP List"

    # add SCP info to provider_info_df
    provider_info_df = pd.concat((provider_info_df, SCP_df), ignore_index=True)
    del SCP_current, SCP_closed, SCP_df

    # standardise postcodes
    provider_info_df["POSTCODE"] = (
        provider_info_df["POSTCODE"].str.replace(" ", "").str.upper()
    )

    # infer LA based on provider's postcode. this does not necessarily match what's in the file!
    provider_info_df[["LA_CODE_INFERRED", "LA_NAME_INFERRED"]] = (
        merge_postcodes(provider_info_df, "POSTCODE")
        .merge(la_df, how="left", left_on="laua", right_on="LTLA21CD")
        .loc[:, ["UTLA21CD", "UTLA21NM"]]
    )

    logger.info(f"Provider info dataframe successfully created {sc.t}")
    return provider_info_df


def scpch_provider_info_table(scpch: UploadedFile):
    """
    inputs:
    Combined CH (childrens homes) and SCP (social care providers) lists as the files' contents as passed in by the frontend

    returns:
    provider_info_df is a dataframe
    (*) it will be stored in dfs['metadata']['provider_info'] if it has been uploaded
    (*) if it's not there, then  return {} for rules requiring it
    (*) the columns will be ['URN', 'PLACE_CODES', 'PROVIDER_CODES', 'REG_END', 'POSTCODE', 'LA_CODE']:
    (*) all cols will be strings (object dtype) except REG_END which will be datetime
        - URN:
            URN of providers/homes, used for merging if there is more htan one list.
        - PLACE_CODES and PROVIDER_CODES:
            strings of codes separated by commas: ['PR4', 'PR1,PR2', etc..]
        - REG_END:
            date provider should have closed (usually blank) - note its type will already be datetime64
        - POSTCODE:
            postcode - upper-cased, spaces removed
        - LA_CODE_INFERRED and LA_NAME_INFERRED:
            utla code and utla name - obtained from la_df by matching on provider postcode
            (!) These may differ from the LA named in the files, either due to formatting, or if they serve
            different LA to where they are located. Rule descriptions should mention this caveat.
        - LA_NAME_FROM_FILE
            LA name from uploaded files.
    """
    if not isinstance(scpch, str):
        if not isinstance(scpch["file_content"], bytes):
            scpch_bytes = scpch["file_content"].tobytes()
        else:
            scpch_bytes = scpch["file_content"]
    else:
        scpch_bytes = scpch

    provider_info_cols = [
        "URN",
        "LA_NAME_FROM_FILE",
        "PLACE_CODES",
        "PROVIDER_CODES",
        "REG_END",
        "POSTCODE",
    ]

    scpch_cols = [
        "urn",
        "local authority",
        "placement code",
        "placement provider code",
        "deregistration date",
        "setting address postcode",
    ]
    logger.info(f"URN lookup bytes recieved. Reading excel files... {sc.t}")

    scpch_providers = pd.read_excel(scpch_bytes, sheet_name=None, engine="openpyxl")
    # Checks to see if it's the one sheet or two sheet version
    if len(scpch_providers) == 1:
        # next iter has a lower memory overhead than extracting the first element via a list
        # when we don't want to hard code the sheet names
        scpch_providers = next(iter(scpch_providers.values()))
        scpch_providers.columns = scpch_providers.columns.str.lower()
    if len(scpch_providers) == 2:
        scpch_iter = iter(scpch_providers.values())
        scpch_1, scpch_2 = next(scpch_iter), next(scpch_iter)

        scpch_2.columns = scpch_2.columns.str.lower()
        scpch_1.columns = scpch_1.columns.str.lower()

        # Supported accomodation has the placement code K3 (I believe)
        scpch_2["placement code"] = "K3"

        scpch_2["deregistration date"] = scpch_2["closed date"]

        if "placement provider code" not in scpch_2.columns:
            scpch_2["placement provider code"] = "PR4"

        scpch_2 = scpch_2[
            [
                "urn",
                "provider local authority",
                "placement code",
                "placement provider code",
                "deregistration date",
                "setting address postcode",
            ]
        ]
        scpch_providers = pd.concat([scpch_1, scpch_2])

    logger.debug(
        f"Reading SCP/CH provider info from excel done. cols:{scpch_providers.columns} {sc.t}"
    )

    try:
        scpch_providers = scpch_providers[scpch_cols[:]]
    except KeyError:
        raise UploadError(
            f'Failed to find required columns in Childrens Homes list "Provider information"'
            f' sheet. Expected: {", ".join(scpch_cols[:])}'
        )
    scpch_df = scpch_providers
    del scpch_providers

    scpch_df["source"] = "Combined SCPCH List"
    scpch_df["placement provider code"] = scpch_df[
        "placement provider code"
    ].str.replace("/", ",")
    provider_info_df = scpch_df.rename(
        columns=dict(zip(scpch_cols, provider_info_cols))
    )
    del scpch_df
    logger.info(f"CH dataframe complete. Creating SCP dataframe {sc.t}")

    # standardise postcodes
    provider_info_df["POSTCODE"] = (
        provider_info_df["POSTCODE"].str.replace(" ", "").str.upper()
    )

    # infer LA based on provider's postcode. this does not necessarily match what's in the file!
    provider_info_df[["LA_CODE_INFERRED", "LA_NAME_INFERRED"]] = (
        merge_postcodes(provider_info_df, "POSTCODE")
        .merge(la_df, how="left", left_on="laua", right_on="LTLA21CD")
        .loc[:, ["UTLA21CD", "UTLA21NM"]]
    )

    logger.info(f"Provider info dataframe successfully created {sc.t}")
    return provider_info_df


def read_files(files: Union[str, Path]) -> List[UploadedFile]:
    uploaded_files: List[_BufferedUploadedFile] = []
    for filename in files:
        uploaded_files.append(
            _BufferedUploadedFile(file=filename, name=filename, description="This year")
        )
    return uploaded_files


def capitalise_object_dtype_cols(df) -> pd.DataFrame:
    """This function takes in a pandas dataframe and capitalizes all the strings found in it."""
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.upper()
    return df


def all_cols_to_object_dtype(df) -> pd.DataFrame:
    """This function converts all columns to object dtype."""
    for col in df.columns:
        if df.dtypes[col] != object:
            df[col] = df[col].values.astype(object)
    return df


def read_csvs_from_text(raw_files: List[UploadedFile]) -> Dict[str, DataFrame]:
    def _get_file_type(df) -> str:
        for table_name, expected_columns in column_names.items():
            if set(df.columns) == set(expected_columns):
                logger.info(f"Loaded {table_name} from CSV. ({len(df)} rows)")
                return table_name
        else:
            raise UploadError(
                f"Failed to match provided data ({list(df.columns)}) to known column names!"
            )

    files = {}
    for file_data in raw_files:
        csv_file = BytesIO(file_data["file_content"])
        # pd.read_csv on utf-16 files will raise a UnicodeDecodeError. This block prints a descriptive error message if that happens.
        try:
            max_cols = max([len(cols) for cols in column_names.values()])
            df = pd.read_csv(
                csv_file,
                converters={
                    i: lambda s: str(s) if s != "" else nan for i in range(max_cols)
                },
            )

        except UnicodeDecodeError:
            # raw_files is a list of files of type UploadedFile(TypedDict) whose instance is a dictionary containing the fields name, file_content, Description.
            # TODO: attempt to identify files that couldnt be decoded at this point; continue; then raise the exception outside the for loop, naming the uploaded filenames
            raise UploadError(
                f"Failed to decode one or more files. Try opening the text "
                f"file(s) in Notepad, then 'Saving As...' with the UTF-8 encoding"
            )
        # arrange column data types
        logger.debug("+" * 50)
        logger.debug("DF DATATYPES BEFORE CONVERSION", df.dtypes)
        df = all_cols_to_object_dtype(df)
        logger.debug("AFTER CONVERSION BEFORE CAPITALISING", df.dtypes)
        # capitalize all string input
        df = capitalise_object_dtype_cols(df)
        logger.debug("DF DATATYPES AFTER CAPITALISING", df.dtypes)

        file_name = _get_file_type(df)

        if "This year" in file_data["description"]:
            name = file_name
        elif "Prev year" in file_data["description"]:
            name = file_name + "_last"
        else:
            raise UploadError(
                f'Unrecognized file description {file_data["description"]}'
            )

        files[name] = df
        logger.debug("DF NAME: ", name)
        logger.debug("+" * 50)

    # Adding UASC column to Header table
    for header_name, uasc_name in (("Header", "UASC"), ("Header_last", "UASC_last")):
        if header_name in files and uasc_name in files:
            header = files[header_name]
            uasc = files[uasc_name]
            merge_indicator = header.merge(
                uasc, how="left", on="CHILD", indicator=True
            )["_merge"]

            header.loc[merge_indicator == "both", "UASC"] = "1"
            header.loc[merge_indicator == "left_only", "UASC"] = "0"

    return files


def read_xml_from_text(xml_string) -> Dict[str, DataFrame]:
    header_df = []
    episodes_df = []
    uasc_df = []
    oc2_df = []
    oc3_df = []
    ad1_df = []
    reviews_df = []
    sbpfa_df = []
    prev_perm_df = []
    missing_df = []

    def read_data(table):
        # The CHILDID tag needs to be renamed to CHILD to match the CSV
        # The PL tag needs to be renamed to PLACE to match the CSV
        conversions = {
            "CHILDID": "CHILD",
            "PL": "PLACE",
        }
        return {
            conversions.get(node.tag, node.tag): node.text
            for node in table.iter()
            if len(node) == 0
        }

    def get_fields_for_table(all_data, table_name):
        def read_value(k):
            val = all_data.get(k, None)
            if val is None:
                return nan
            if not isinstance(val, str):
                logger.warning(
                    f"Got a non-string thing reading {table_name}:{k} from xml -- got {val}, of type {type(val)}"
                )
            return val

        # Add UASC column to Header and Header_last tables
        cols = column_names[table_name]
        if table_name in ["Header", "Header_last"]:
            cols = cols + ["UASC"]

        return pd.Series({k: read_value(k) for k in cols}, dtype=object)

    for child in ET.fromstring(xml_string):
        all_data = read_data(child)
        header_df.append(get_fields_for_table(all_data, "Header"))
        if all_data.get("UASC", None) is not None:
            uasc_df.append(get_fields_for_table(all_data, "UASC"))
        if all_data.get("IN_TOUCH", None) is not None:
            oc3_df.append(get_fields_for_table(all_data, "OC3"))
        if all_data.get("DATE_INT", None) is not None:
            ad1_df.append(get_fields_for_table(all_data, "AD1"))
        for table in child:
            if table.tag == "EPISODE":
                data = read_data(table)
                episodes_df.append(
                    get_fields_for_table({**all_data, **data}, "Episodes")
                )
            elif table.tag == "HEADER":
                for child_table in table:
                    if child_table.tag == "AREVIEW":
                        data = read_data(child_table)
                        reviews_df.append(
                            get_fields_for_table({**all_data, **data}, "Reviews")
                        )
                    elif child_table.tag == "AMISSING":
                        data = read_data(child_table)
                        missing_df.append(
                            get_fields_for_table({**all_data, **data}, "Missing")
                        )
                    elif child_table.tag == "OC2":
                        data = read_data(child_table)
                        oc2_df.append(get_fields_for_table({**all_data, **data}, "OC2"))
                    elif child_table.tag == "PERMANENCE":
                        data = read_data(child_table)
                        prev_perm_df.append(
                            get_fields_for_table({**all_data, **data}, "PrevPerm")
                        )
                    elif child_table.tag == "AD_PLACED":
                        data = read_data(child_table)
                        sbpfa_df.append(
                            get_fields_for_table({**all_data, **data}, "PlacedAdoption")
                        )
                    elif child_table.tag == "SW_EPISODE":
                        data = read_data(child_table)
                        sbpfa_df.append(
                            get_fields_for_table({**all_data, **data}, "PlacedAdoption")
                        )

    data = {
        "Header": pd.DataFrame(header_df),
        "Episodes": pd.DataFrame(episodes_df),
        "UASC": pd.DataFrame(uasc_df),
        "Reviews": pd.DataFrame(reviews_df),
        "OC2": pd.DataFrame(oc2_df),
        "OC3": pd.DataFrame(oc3_df),
        "AD1": pd.DataFrame(ad1_df),
        "PlacedAdoption": pd.DataFrame(sbpfa_df),
        "PrevPerm": pd.DataFrame(prev_perm_df),
        "Missing": pd.DataFrame(missing_df),
        "sw_episodes": pd.DataFrame(sw_episodes_df),
        "DoLo": pd.DataFrame(dolo_df),
    }

    # capitalize string columns
    for df in data.values():
        df = all_cols_to_object_dtype(df)
        df = capitalise_object_dtype_cols(df)

    names_and_lengths = ", ".join(f"{t}: {len(data[t])} rows" for t in data)
    logger.info(f"Tables created from XML -- {names_and_lengths}")
    return data


def combined_ch_scp_check(excel_to_check):
    """
    Checks whether the file uploaded to the front end in the Children's home box is a CH list or a combined SPC/CH list.
    Only runs in instances where the number fo files uploaded in the SCP/CH boxes is one.
    """
    if isinstance(excel_to_check, bytes):
        CH_bytes = excel_to_check
    elif isinstance(excel_to_check, dict):
        if isinstance(excel_to_check["file_content"], bytes):
            CH_bytes = excel_to_check["file_content"]
        elif not isinstance(excel_to_check["file_content"], bytes):
            CH_bytes = excel_to_check["file_content"].tobytes()
    else:
        logger.info(
            f"Something is wrong with your 'Children's Home' or 'Social Care Providers' lists, check they're uploaded in the right boxes \
                    \n and that the column names are correct. {sc.t}"
        )
        raise UploadError(
            "Only one 'Children's Home' or 'Social Care Providers' list detected in upload,"
            "but it doesn't appear to be a combined list."
            "Please upload lists from Ofsted into their respective boxes above."
        )
    input_file = pd.read_excel(CH_bytes, engine="openpyxl", sheet_name=None)

    if (set(input_file.keys()) == set(["Providers", "SA providers"])) | (
        set(input_file.keys()) == set(["Providers", "SA Providers"])
    ):
        logger.info(
            f"'Childrens home' and 'Social Care Providers' lists detected across two sheets of Excel workbook. {sc.t}"
        )
        return True
    elif len(input_file.keys()) == 1:
        df = next(iter(input_file.values()))
        df.columns = df.columns.str.lower()
        if "provider type" not in df.columns:
            logger.info(
                f"Something is wrong with your 'Children's Home' or 'Social Care Providers' lists, check they're uploaded in the right boxes \
                        \n and that the column names are correct. {sc.t}"
            )
            raise UploadError(
                "Only one 'Children's Home' or 'Social Care Providers' list detected in upload,"
                "but it doesn't appear to be a combined list."
                "Please upload lists from Ofsted into their respective boxes above."
            )
        if (len(df["provider type"]) > 1) & (
            "Children's Home" in df["provider type"].values
        ):
            logger.info(
                f"Combined 'Childrens home' and 'Social Care Providers' lists detected. {sc.t}"
            )
            return True
        if (len(df["provider type"]) == 1) & (
            "Children's Home" in df["provider type"].values
        ):
            logger.info(
                f"'Children's home' list as only CH data file in upload detected. {sc.t}"
            )
            raise UploadError(
                "Only one 'Children's Home' or 'Social Care Providers' list detected in upload,"
                "but it doesn't appear to be a combined list."
                "Please upload lists from Ofsted into their respective boxes above."
            )
        else:
            logger.info(
                f"Something is wrong with your 'Children's Home' or 'Social Care Providers' lists, check they're uploaded in the right boxes \
                        \n and that the column names are correct. {sc.t}"
            )
            raise UploadError(
                "Only one 'Children's Home' or 'Social Care Providers' list detected in upload,"
                "but it doesn't appear to be a combined list."
                "Please upload lists from Ofsted into their respective boxes above."
            )
    else:
        logger.info(
            f"Something is wrong with your 'Children's Home' or 'Social Care Providers' lists, check they're of the correct file type. {sc.t}"
        )
        raise UploadError(
            "Only one 'Children's Home' or 'Social Care Providers' list detected in upload,"
            "but the file cannot be read for some reason. Check it's the correct file type."
        )
