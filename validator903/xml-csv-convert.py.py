import collections.abc
from pathlib import Path

import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Union, Dict, Iterator,TypedDict

from pandas import DataFrame

import logging
logger = logging.getLogger(__name__)


column_names = {
    'Header': ['CHILD', 'SEX', 'DOB', 'ETHNIC', 'UPN', 'MOTHER', 'MC_DOB'],
    'Episodes': ['CHILD', 'DECOM', 'RNE', 'LS', 'CIN', 'PLACE', 'PLACE_PROVIDER', 'DEC', 'REC', 'REASON_PLACE_CHANGE',
                 'HOME_POST', 'PL_POST', 'URN'],
    'Reviews': ['CHILD', 'DOB', 'REVIEW', 'REVIEW_CODE'],
    'UASC': ['CHILD', 'SEX', 'DOB', 'DUC'],
    'OC2': ['CHILD', 'DOB', 'SDQ_SCORE', 'SDQ_REASON', 'CONVICTED', 'HEALTH_CHECK',
            'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE',
            'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    'OC3': ['CHILD', 'DOB', 'IN_TOUCH', 'ACTIV', 'ACCOM'],
    'AD1': ['CHILD', 'DOB', 'DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR'],
    'PlacedAdoption': ['CHILD', 'DOB', 'DATE_PLACED', 'DATE_PLACED_CEASED', 'REASON_PLACED_CEASED'],
    # Note: for PrevPerm, LA_PERM will usually be blank and shouldn't be used directly
    'PrevPerm': ['CHILD', 'DOB', 'PREV_PERM', 'LA_PERM', 'DATE_PERM'],
    'Missing': ['CHILD', 'DOB', 'MISSING', 'MIS_START', 'MIS_END'],
}

class UploadedFile(TypedDict):
    name: str
    fileText: bytes
    description: str

class UploadException(Exception):
    pass

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
        if extensions[0] == 'xml':
            return read_xml_from_text(raw_files[0]['fileText'])
        else:
            raise UploadException(f'Unknown file type {extensions[0]} found.')


#def read_files(files: Union[str, Path]) -> List[UploadedFile]:
#    uploaded_files: List[_BufferedUploadedFile] = []
#    for filename in files:
#        uploaded_files.append(_BufferedUploadedFile(file=filename, name=filename, description="This year"))
#    return uploaded_files

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
    names_and_lengths = ', '.join(f'{t}: {len(data[t])} rows' for t in data)
    logger.info(f'Tables created from XML -- {names_and_lengths}')

    return data

    # convert DataFrames to csv format
    for key, df in data.iteritems():
      csv_file = df.to_csv(key + '.csv')
    
