import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO
from typing import List
from .types import UploadException
from .config import column_names

def read_from_text(raw_files):
    if len(raw_files) == 0:
        raise UploadException('No files uploaded!')

    extensions = list(set([f["name"][-3:].lower() for f in raw_files]))
    if len(extensions) != 1:
        raise UploadException(f'Mix of CSV and XML files found ({extensions})! Please reupload.')
    else:
        if extensions[0] == 'csv':
            return read_csvs_from_text(raw_files)
        elif extensions[0] == 'xml':
            if len(raw_files) != 1:
                raise UploadException('Only reading from a single XML file is supported.')
            return read_xml_from_text(raw_files[0]['fileText'])
        else:
            raise UploadException(f'Unknown file type {extensions[0]} found.')

def read_csvs_from_text(raw_files: List):
    def _get_file_type(df):
        for table_name, expected_columns in column_names.items():
            if set(df.columns) == set(expected_columns):
                return table_name
        else:
            raise UploadException(f'Failed to match provided data ({list(df.columns)}) to known column names!')

    files = {}
    for file_data in raw_files:
        csv_file = StringIO(file_data["fileText"])
        df = pd.read_csv(csv_file)

        files[_get_file_type(df)] = df

    return files

def read_xml_from_text(xml_string):
    header_df = []
    episodes_df = []
    uasc_df = []

    def read_data(table):
        # The CHILDID tag needs to be renamed to CHILD to match the CSV
        return  {
            (node.tag if node.tag != 'CHILDID' else 'CHILD'): node.text 
            for node in table.iter() if len(node) == 0
        }

    for child in ET.fromstring(xml_string):
        all_data = read_data(child)
        header_df.append(pd.Series({k: all_data.get(k, None) for k in column_names['Header']}))
        if all_data.get('DUC', None) is not None:
            uasc_df.append(pd.Series({k: all_data.get(k, None) for k in column_names['UASC']}))
        for table in child:
            if table.tag == 'EPISODE':
                data = read_data(table)
                episodes_df.append(pd.Series({k: {**all_data, **data}.get(k, None) for k in column_names['Episodes']}))

    return {
        'Header': pd.DataFrame(header_df),
        'Episodes': pd.DataFrame(episodes_df),
        'UASC': pd.DataFrame(uasc_df),
    }
