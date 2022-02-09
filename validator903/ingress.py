import collections.abc
from pathlib import Path

import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import List, Union, Dict, Iterator, Tuple

from pandas import DataFrame
from numpy import nan
from .types import UploadError, UploadedFile
from .config import column_names

import logging
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)  # uncomment if you want to see debug messages

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
        elif k == "fileText":
            with open(self.file, 'rb') as file:
                return file.read()
        else:
            raise AttributeError(f'{k} not found')

    def __len__(self) -> int:
        return 3

    def __iter__(self) -> Iterator:
        pass


def read_from_text(raw_files: List[UploadedFile]) -> Tuple[Dict[str, DataFrame], str]:
    """
    Reads from a raw list of files passed from javascript. These files are of
    the form e.g.
    [
        {name: 'filename.csv', fileText: <file contents>, description: <upload metadata>}
    ]

    This function will try to catch most basic upload errors, and dispatch other errors
    to either the csv or xml reader based on the file extension.
    """

    CH_uploaded = [f for f in raw_files if f['description'] == 'CH lookup']
    SCP_uploaded = [f for f in raw_files if f['description'] == 'SCP lookup']
    num_of_CH_and_SCP = (len(CH_uploaded), len(SCP_uploaded))

    logger.info(f'#CH: {num_of_CH_and_SCP[0]}, #SCP:{num_of_CH_and_SCP[1]}')

    if max(num_of_CH_and_SCP) > 1:
        raise UploadError(
            f"{num_of_CH_and_SCP[0]} (Children's Homes List) and {num_of_CH_and_SCP[1]} (Social Care Providers List) "
            f"URN lookup tables were loaded - Please only load a single file in each box."
        )
    elif set(num_of_CH_and_SCP) == {0, 1}:
        raise UploadError(
            "Please load both the latest 'Children's Homes' and 'Social Care Providers' lists "
            "from Ofsted into their respective boxes above."
        )
    elif set(num_of_CH_and_SCP) == {1}:
        (CH_uploaded,) = CH_uploaded
        (SCP_uploaded,) = SCP_uploaded
        construct_URN_lookup_table(CH=CH_uploaded, SCP=SCP_uploaded)

    raw_files = [f for f in raw_files
                 if f['description'] not in ('CH lookup', 'SCP lookup')]

    extensions = list(set([f["name"].split('.')[-1].lower() for f in raw_files]))
    if len(raw_files) == 0:
        raise UploadError('No SSDA 903 files uploaded!')
    elif len(extensions) > 1:
        raise UploadError(f'Mix of CSV and XML files found ({extensions})! Please reupload.')
    else:
        if extensions[0] == 'csv':
            return read_csvs_from_text(raw_files), 'csv'
        elif extensions[0] == 'xml':
            return read_xml_from_text(raw_files[0]['fileText']), 'xml'
        else:
            raise UploadError(f'Unknown file type {extensions[0]} found.')


def construct_URN_lookup_table(CH, SCP):
    logger.info('type:' + str(type(CH['fileText'])))
    logger.info('filtext'+ str(CH['fileText']))
    logger.info('dir(FILETEXT):''\n' + str(dir(CH['fileText'])))

    # TODO: read only the necessary data; hopefully improve performance
    CH_ = pd.read_excel(CH['fileText'].tobytes(), sheet_name=None, engine='openpyxl')
    SCP = pd.read_excel(SCP['fileText'].tobytes(), sheet_name=None, engine='openpyxl')
    logger.info(f'{type(CH)}, {CH}')
    logger.info(f'{[i.shape for i in CH.items()]}')
    return


def read_files(files: Union[str, Path]) -> List[UploadedFile]:
    uploaded_files: List[_BufferedUploadedFile] = []
    for filename in files:
        uploaded_files.append(_BufferedUploadedFile(file=filename, name=filename, description="This year"))
    return uploaded_files

def capitalise_object_dtype_cols(df) -> pd.DataFrame:
    '''This function takes in a pandas dataframe and capitalizes all the strings found in it.'''
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].str.upper()
    return df

def all_cols_to_object_dtype(df) -> pd.DataFrame:
    '''This function converts all columns to object dtype.'''
    for col in df.columns:
        if df.dtypes[col] != object:
            df[col] = df[col].values.astype(object)
    return df

def read_csvs_from_text(raw_files: List[UploadedFile]) -> Dict[str, DataFrame]:

    def _get_file_type(df) -> str:
        for table_name, expected_columns in column_names.items():
            if set(df.columns) == set(expected_columns):
                logger.info(f'Loaded {table_name} from CSV. ({len(df)} rows)')
                return table_name
        else:
            raise UploadError(f'Failed to match provided data ({list(df.columns)}) to known column names!')

    files = {}
    for file_data in raw_files:
        csv_file = BytesIO(file_data["fileText"])
        # pd.read_csv on utf-16 files will raise a UnicodeDecodeError. This block prints a descriptive error message if that happens.
        try:
            max_cols = max([len(cols) for cols in column_names.values()])
            df = pd.read_csv(csv_file, converters={i: lambda s: str(s) if s != '' else nan
                                                   for i in range(max_cols)})

        except UnicodeDecodeError:
            # raw_files is a list of files of type UploadedFile(TypedDict) whose instance is a dictionary containing the fields name, fileText, Description.
            # TODO: attempt to identify files that couldnt be decoded at this point; continue; then raise the exception outside the for loop, naming the uploaded filenames
            raise UploadError(f"Failed to decode one or more files. Try opening the text "
                                  f"file(s) in Notepad, then 'Saving As...' with the UTF-8 encoding")
        # arrange column data types
        logger.debug('+'*50)
        logger.debug('DF DATATYPES BEFORE CONVERSION', df.dtypes)
        df = all_cols_to_object_dtype(df)
        logger.debug('AFTER CONVERSION BEFORE CAPITALISING', df.dtypes)
        # capitalize all string input
        df = capitalise_object_dtype_cols(df)
        logger.debug('DF DATATYPES AFTER CAPITALISING', df.dtypes)

        file_name = _get_file_type(df)

        if 'This year' in file_data['description']:
            name = file_name
        elif 'Prev year' in file_data['description']:
            name = file_name + '_last'
        else:
            raise UploadError(f'Unrecognized file description {file_data["description"]}')

        files[name] = df
        logger.debug('DF NAME: ', name)
        logger.debug('+'*50)

    # Adding UASC column to Header table
    for header_name, uasc_name in (('Header', 'UASC'), ('Header_last', 'UASC_last')):
        if header_name in files and uasc_name in files:
            header = files[header_name]
            uasc = files[uasc_name]
            merge_indicator = header.merge(uasc, how='left', on='CHILD', indicator=True)['_merge']

            header.loc[merge_indicator == 'both', 'UASC'] = '1'
            header.loc[merge_indicator == 'left_only', 'UASC'] = '0'

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
            'CHILDID': 'CHILD',
            'PL': 'PLACE',
        }
        return {
            conversions.get(node.tag, node.tag): node.text 
            for node in table.iter() if len(node) == 0
        }

    def get_fields_for_table(all_data, table_name):
        def read_value(k):
            val = all_data.get(k, None)
            if val is None:
                return nan
            if not isinstance(val, str):
                logger.warning(
                    f'Got a non-string thing reading {table_name}:{k} from xml -- got {val}, of type {type(val)}'
                )
            return val
        
        # Add UASC column to Header and Header_last tables
        cols = column_names[table_name]
        if table_name in ['Header', 'Header_last']:
            cols = cols + ['UASC']

        return pd.Series({k: read_value(k) for k in cols}, dtype=object)

    for child in ET.fromstring(xml_string):
        all_data = read_data(child)
        header_df.append(get_fields_for_table(all_data, 'Header'))
        if all_data.get('UASC', None) is not None:
            uasc_df.append(get_fields_for_table(all_data, 'UASC'))
        if all_data.get('IN_TOUCH', None) is not None:
            oc3_df.append(get_fields_for_table(all_data, 'OC3'))
        if all_data.get('DATE_INT', None) is not None:
            ad1_df.append(get_fields_for_table(all_data, 'AD1'))
        for table in child:
            if table.tag == 'EPISODE':
                data = read_data(table)
                episodes_df.append(get_fields_for_table({**all_data, **data}, 'Episodes'))
            elif table.tag == 'HEADER':
                for child_table in table:
                    if child_table.tag == 'AREVIEW':
                        data = read_data(child_table)
                        reviews_df.append(get_fields_for_table({**all_data, **data}, 'Reviews'))
                    elif child_table.tag == 'AMISSING':
                        data = read_data(child_table)
                        missing_df.append(get_fields_for_table({**all_data, **data}, 'Missing'))
                    elif child_table.tag == 'OC2':
                        data = read_data(child_table)
                        oc2_df.append(get_fields_for_table({**all_data, **data}, 'OC2'))
                    elif child_table.tag == 'PERMANENCE':
                        data = read_data(child_table)
                        prev_perm_df.append(get_fields_for_table({**all_data, **data}, 'PrevPerm'))
                    elif child_table.tag == 'AD_PLACED':
                        data = read_data(child_table)
                        sbpfa_df.append(get_fields_for_table({**all_data, **data}, 'PlacedAdoption'))

    data = {
        'Header': pd.DataFrame(header_df),
        'Episodes': pd.DataFrame(episodes_df),
        'UASC': pd.DataFrame(uasc_df),
        'Reviews': pd.DataFrame(reviews_df),
        'OC2': pd.DataFrame(oc2_df),
        'OC3': pd.DataFrame(oc3_df),
        'AD1': pd.DataFrame(ad1_df),
        'PlacedAdoption': pd.DataFrame(sbpfa_df),
        'PrevPerm': pd.DataFrame(prev_perm_df),
        'Missing': pd.DataFrame(missing_df),
    }

    # capitalize string columns
    for df in data.values():
        df = all_cols_to_object_dtype(df)
        df = capitalise_object_dtype_cols(df)

    names_and_lengths = ', '.join(f'{t}: {len(data[t])} rows' for t in data)
    logger.info(f'Tables created from XML -- {names_and_lengths}')
    return data
