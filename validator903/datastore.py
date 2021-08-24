from copy import copy
import pandas as pd
from .ingress import read_postcodes

def create_datastore(data, metadata):
    """
    Returns a dictionary with keys for
    - Every table name in config.py
    - Every table name again, with the suffix '_last', if last years data was uploaded.
    - A 'metadata' key, which links to a nested dictionary with
      - 'postcodes' - a postcodes csv, with columns "laua" (LA code), "lat", "long" (coordinates) and "pcd" (the postcode)
      - 'localAuthority' - the code of the local authority (long form)

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
    # There should be no duplicates - but to future-proof an error file we can drop them here anyway.
    metadata['postcodes'] = {
        p.pcd.replace(' ', ''): p for p in metadata['postcodes'].itertuples()
    }
    return metadata

def _add_postcode_derived_fields(episodes_df, postcodes):
    print('Adding postcodes...')

    def get_la(pcd):
        try:
            return postcodes[pcd.replace(' ', '')].laua
        except (KeyError, AttributeError):
            return pd.NA

    episodes_df['HOME_LA'] = episodes_df['HOME_POST'].apply(get_la)
    episodes_df['PL_LA'] = episodes_df['PL_POST'].apply(get_la)

    # The indexes remain the same post merge as the length of the dataframes doesn't change.
    episodes_df['PL_LOCATION'] = 'IN'
    episodes_df.loc[episodes_df['HOME_LA'] != episodes_df['PL_LA'], 'PL_LOCATION'] = 'OUT'
    episodes_df.loc[episodes_df['HOME_LA'].isna(), 'PL_LOCATION'] = pd.NA
    print('Done adding postcodes!')

    return episodes_df



# TODO: Write tests for this
# TODO: Add the derived fields to episodes