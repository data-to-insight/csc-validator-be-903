import pandas as pd
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from io import StringIO, BytesIO
from typing import List
from .types import UploadException, UploadedFile
from .config import column_names

def read_from_text(raw_files: List[UploadedFile]):
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

def read_csvs_from_text(raw_files: List[UploadedFile]):
    def _get_file_type(df) -> str:
        for table_name, expected_columns in column_names.items():
            if set(df.columns) == set(expected_columns):
                return table_name
        else:
            raise UploadException(f'Failed to match provided data ({list(df.columns)}) to known column names!')

    files = {}
    for file_data in raw_files:
        csv_file = StringIO(file_data["fileText"])
        df = pd.read_csv(csv_file)
        file_name = _get_file_type(df)
        if 'This year' in file_data['description']:
            name = file_name
        elif 'Last year' in file_data['description']:
            name = file_name + '_last'
        else:
            raise UploadException(f'Unrecognized file description {file_data["description"]}')

        files[name] = df

    return files

def read_xml_from_text(xml_string):
    header_df = []
    episodes_df = []
    uasc_df = []
    oc3_df = []
    ad1_df = []
    reviews_df = []
    sbpfa_df = []

    def read_data(table):
        # The CHILDID tag needs to be renamed to CHILD to match the CSV
        return  {
            (node.tag if node.tag != 'CHILDID' else 'CHILD'): node.text 
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
                    elif child_table.tag == 'AD_PLACED':
                        data = read_data(child_table)
                        sbpfa_df.append(get_fields_for_table({**all_data, **data}, 'PlacedAdoption'))

    return {
        'Header': pd.DataFrame(header_df),
        'Episodes': pd.DataFrame(episodes_df),
        'UASC': pd.DataFrame(uasc_df),
        'Reviews': pd.DataFrame(reviews_df),
        'OC3': pd.DataFrame(oc3_df),
        'AD1': pd.DataFrame(ad1_df),
        'PlacedAdoption': pd.DataFrame(sbpfa_df),
    }

def read_postcodes(zipped_csv_bytes):
    with ZipFile(BytesIO(zipped_csv_bytes)) as unzipped:
        with unzipped.open('postcodes.csv') as f:
            return pd.read_csv(f)