import collections.abc
from pathlib import Path

import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import List, Union, Dict, Iterator

from pandas import DataFrame

from .types import UploadException, UploadedFile
from .config import column_names

import logging
logger = logging.getLogger(__name__)


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


def read_from_text(raw_files: List[UploadedFile]) -> Dict[str, DataFrame]:
    """
    Reads from a raw list of files passed from javascript. These files are of
    the form e.g.
    [
        {name: 'filename.csv', fileText: <file contents>, description: <upload metadata>}
    ]

    This function will try to catch most basic upload errors, and dispatch other errors
    to either the csv or xml reader based on the file extension.
    """
    if len(raw_files) == 0:
        raise UploadException('No files uploaded!')

    extensions = list(set([f["name"][-3:].lower() for f in raw_files]))
    if len(extensions) != 1:
        raise UploadException(f'Mix of CSV and XML files found ({extensions})! Please reupload.')
    else:
        if extensions[0] == 'csv':
            return read_csvs_from_text(raw_files)
        elif extensions[0] == 'xml':
            return read_xml_from_text(raw_files[0]['fileText'])
        else:
            raise UploadException(f'Unknown file type {extensions[0]} found.')


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

def read_csvs_from_text(raw_files: List[UploadedFile]) -> Dict[str, DataFrame]:

    def _get_file_type(df) -> str:
        for table_name, expected_columns in column_names.items():
            if set(df.columns) == set(expected_columns):
                logger.info(f'Loaded {table_name} from CSV. ({len(df)} rows)')
                return table_name
        else:
            raise UploadException(f'Failed to match provided data ({list(df.columns)}) to known column names!')

    files = {}
    for file_data in raw_files:
        csv_file = BytesIO(file_data["fileText"])
        # pd.read_csv on utf-16 files will raise a UnicodeDecodeError. This block prints a descriptive error message if that happens.
        try:
            df = pd.read_csv(csv_file)
        except UnicodeDecodeError:
            # raw_files is a list of files of type UploadedFile(TypedDict) whose instance is a dictionary containing the fields name, fileText, Description.
            # TODO: attempt to identify files that couldnt be decoded at this point; continue; then raise the exception outside the for loop, naming the uploaded filenames
            raise UploadException(f"Failed to decode one or more files. Try opening the text "
                                f"file(s) in Notepad, then 'Saving As...' with the UTF-8 encoding")

        # capitalize all string input
        df = capitalise_object_dtype_cols(df)

        file_name = _get_file_type(df)
        if 'This year' in file_data['description']:
            name = file_name
        elif 'Prev year' in file_data['description']:
            name = file_name + '_last'
        else:
            raise UploadException(f'Unrecognized file description {file_data["description"]}')

        files[name] = df

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
        return  {
            conversions.get(node.tag, node.tag): node.text 
            for node in table.iter() if len(node) == 0
        }

    def get_fields_for_table(all_data, table_name):
        def read_value(k):
            val = all_data.get(k, None)
            try:
                val = int(val)
            except:
                pass
            return val
        return pd.Series({k: read_value(k) for k in column_names[table_name]}) 

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

    data =  {
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
      df = capitalise_object_dtype_cols(df)

    names_and_lengths = ', '.join(f'{t}: {len(data[t])} rows' for t in data)
    logger.info(f'Tables created from XML -- {names_and_lengths}')
    return data
