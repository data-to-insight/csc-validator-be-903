import datetime
import logging
import os
from pathlib import Path
from typing import Dict, Any

import numpy as np
from copy import copy
import pandas as pd
import qlacref_authorities
from pandas import DataFrame
from qlacref_postcodes import Postcodes

logger = logging.getLogger(__name__)

la_df = pd.DataFrame.from_records(qlacref_authorities.records)
logger.info("Loaded authorities")

# A bit of a hack, but will keep things working
if os.getenv('QLACREF_PC_KEY') is None:
    key_file = Path(__file__).parent.parent / ".qlacref/id_rsa.pub"
    if key_file.is_file():
        logger.warning("Using repository key for pickle signature. "
                       "To stay safe from tampering, set the key path in 'QLACREF_PC_KEY'")
        os.environ['QLACREF_PC_KEY'] = str(key_file.absolute())

postcodes = Postcodes()
logger.info("Initialised Postcodes")


def create_datastore(data: Dict[str, Any], metadata: Dict[str, Any]):
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
    logger.info(', '.join(data.keys()))
    data = copy(data)
    data['metadata'] = _process_metadata(metadata)
    if 'Episodes' in data:
        data['Episodes'] = _add_postcode_derived_fields(
            data['Episodes'], metadata['localAuthority'],
        )
    if 'Episodes_last' in data:
        data['Episodes_last'] = _add_postcode_derived_fields(
            data['Episodes_last'], metadata['localAuthority']
        )
    # quick n dirty fix for weird postcode related columns showing up in episode tables
    for table_name in ['Episodes', 'Episodes_last']:
        if table_name in data:
            data[table_name] = data[table_name].drop(columns={'_14', '_15', '_16', '_17'} & set(data[table_name].columns))


    names_and_lengths = ', '.join(f'{t}: {len(data[t])} rows' for t in data)
    logger.info(f'Datastore created -- {names_and_lengths}')
    return data


def _process_metadata(metadata):
    collection_year = int(metadata['collectionYear'][:4])
    metadata['collection_start'] = datetime.datetime(collection_year, 4, 1)
    metadata['collection_end'] = datetime.datetime(collection_year + 1, 3, 31)
    return metadata


def merge_postcodes(df: DataFrame, postcode_field: str) -> DataFrame:
    df[postcode_field] = df[postcode_field].str.upper()

    key_field = f'__{postcode_field}__first_letter'
    df[key_field] = df[postcode_field].str[0]
    pcs = df[key_field].dropna().unique()

    logger.info(f"Loading the following postcode letters: {pcs}")
    postcodes.load_postcodes(pcs)

    logger.info(f"Adding postcode abbreviations for {postcode_field}")
    pc_abbr_field = f'__{postcode_field}__abbr'
    df[pc_abbr_field] = df[postcode_field].str.replace(' ', '')

    df_merged = df[[pc_abbr_field]].merge(postcodes.dataframe, how='left', left_on=pc_abbr_field, right_on='pcd_abbr')
    del df[key_field]
    del df[pc_abbr_field]

    return df_merged


def _add_postcode_derived_fields(episodes_df, local_authority):
    episodes_df = episodes_df.copy()
    home_details = merge_postcodes(episodes_df, "HOME_POST")
    pl_details = merge_postcodes(episodes_df, "PL_POST")

    # The indexes remain the same post merge as the length of the dataframes doesn't change, so we can set directly.
    pl_details = pl_details.merge(la_df, how='left', left_on='laua', right_on='LTLA21CD')
    episodes_df['PL_LA'] = pl_details['UTLA21CD']

    logger.info(f"Adding IN/OUT")
    episodes_df['PL_LOCATION'] = 'IN'
    episodes_df.loc[episodes_df['PL_LA'].ne(local_authority), 'PL_LOCATION'] = 'OUT'
    episodes_df.loc[episodes_df['PL_LA'].isna(), 'PL_LOCATION'] = pd.NA

    logger.info(f"Calculating distances")
    # This formula is taken straight from the guidance, to get miles between two postcodes
    episodes_df['PL_DISTANCE'] = np.sqrt(
        (home_details['oseast1m'] - pl_details['oseast1m']) ** 2 +
        (home_details['osnrth1m'] - pl_details['osnrth1m']) ** 2
    ) / 1000 / 1.6093
    episodes_df['PL_DISTANCE'] = episodes_df['PL_DISTANCE'].round(decimals=1)

    logger.info(f"Completed postcode calculations")
    return episodes_df


def copy_datastore(data_store):
    """
    This is used for getting a shallow copy that is passed to the validation rules.
    """
    return {k: v.copy(deep=False) if k != 'metadata' else v for k, v in data_store.items()}
