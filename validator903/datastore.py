import datetime
import numpy as np
from copy import copy
import pandas as pd
from .ingress import read_postcodes

def create_datastore(data, metadata):
    """
    Returns a dictionary with keys for
    - Every table name in config.py
    - Every table name again, with the suffix '_last', if last years data was uploaded.
    - A 'metadata' key, which links to a nested dictionary with
      - 'postcodes' - a postcodes csv, with columns "laua" (LA code), "oseast1m", "osnrth1m" (coordinates) and "pcd" (the postcode)
      - 'localAuthority' - the code of the local authority (long form)
      - 'collectionYear' - the collection year string (e.g. '2019/20)

    :param data: Dict of raw DataFrames by name (from config.py) together with the '_last' data.
    :param metadata:
    """
    data = copy(data)
    data['metadata'] = _process_metadata(metadata)
    data['Episodes'] = _add_postcode_derived_fields(data['Episodes'], metadata['postcodes'])
    if 'Episodes_last' in data:
        data['Episodes_last'] = _add_postcode_derived_fields(data['Episodes_last'], metadata['postcodes'])
    return data

def _process_metadata(metadata):
    collection_year = int(metadata['collectionYear'][:4])
    metadata['collection_start'] = datetime.datetime(collection_year, 4, 1)
    metadata['collection_end'] = datetime.datetime(collection_year + 1, 3, 31)
    return metadata

def _add_postcode_derived_fields(episodes_df, postcodes):
    print('Adding postcodes...')
    episodes_df['home_pcd'] = episodes_df['HOME_POST'].str.replace(' ', '')
    home_details = episodes_df[['home_pcd']].merge(postcodes, how='left', left_on='home_pcd', right_on='pcd')
    del episodes_df['home_pcd']

    episodes_df['pl_pcd'] = episodes_df['PL_POST'].str.replace(' ', '')
    pl_details = episodes_df[['pl_pcd']].merge(postcodes, how='left', left_on='pl_pcd', right_on='pcd')
    del episodes_df['pl_pcd']

    # The indexes remain the same post merge as the length of the dataframes doesn't change, so we can set directly.

    episodes_df['HOME_LA'] = home_details['laua']
    episodes_df['PL_LA'] = pl_details['laua']

    episodes_df['PL_LOCATION'] = 'IN'
    episodes_df.loc[episodes_df['HOME_LA'] != episodes_df['PL_LA'], 'PL_LOCATION'] = 'OUT'
    episodes_df.loc[episodes_df['HOME_LA'].isna(), 'PL_LOCATION'] = pd.NA

    # This formula is taken straight from the guidance, to get miles between two postcodes
    episodes_df['PL_DISTANCE'] = np.sqrt(
        (home_details['oseast1m'] - pl_details['oseast1m'])**2 + 
        (home_details['osnrth1m'] - pl_details['osnrth1m'])**2 
    ) / 1000 / 1.6093
    episodes_df['PL_DISTANCE'] = episodes_df['PL_DISTANCE'].round(decimals=1)

    return episodes_df

def copy_datastore(data_store):
    """
    This is used for getting a shallow copy that is passed to the validation rules.
    """
    return {k: v.copy(deep=False) if k != 'metadata' else v for k, v in data_store.items()}
