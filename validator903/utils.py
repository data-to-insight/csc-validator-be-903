import pandas as pd


# might be worth adding 'collection_end' as an argument, though not specified in definition
def add_col_to_episodes_CONTINUOUSLY_LOOKED_AFTER(episodes, collection_start, collection_end):
    """
    adds a True/False column called 'CONTINUOUSLY_LOOKED_AFTER' to the 'Episodes' table,
    which is True if they appear to have been looked after since `collection_start`
    (NB: currently modifies, and returns reference to, the original DataFrame that's passed in)

    implemented as defined in:
    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1023549/CLA_SSDA903_2021-22_Validation_rules_Version_1.2.pdf

    ie. a child is continuously looked after unless they have any episodes which either:
        - end after collection_start with LS is V3/V4
        - end after after collection_start where REC isn't X1
        - begin after collection_start where RNE is S
    """
    eps_copy = episodes.copy()

    # Set datetime types
    collection_start_dt = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
    collection_end_dt = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
    eps_copy['DEC_dt'] = pd.to_datetime(eps_copy['DEC'], format='%d/%m/%Y', errors='coerce')
    eps_copy['DECOM_dt'] = pd.to_datetime(eps_copy['DECOM'], format='%d/%m/%Y', errors='coerce')

    eps_copy['during_year'] = (
            (eps_copy['DECOM_dt'] <= collection_end_dt)
            & ((eps_copy['DEC_dt'] >= collection_start_dt) | eps_copy['DEC_dt'].isna())
    )

    # Find CHILD id's displaying the telltale signs of <LOOKED_AFTER_CONTINUOUSLY> = 'N'
    enters_care = (
        (eps_copy['RNE'] == 'S')
        & (eps_copy['DECOM_dt'] > collection_start_dt)
        & (eps_copy['DECOM_dt'] <= collection_end_dt)
    )
    leaves_care = (
        (eps_copy['REC'] != 'X1')
        & (eps_copy['DEC_dt'] >= collection_start_dt)
        & (eps_copy['DEC_dt'] < collection_end_dt)
    )
    V3_V4_episode = (
        eps_copy['LS'].isin(['V3', 'V4'])
        & eps_copy['during_year']
    )

    # if any episode fits one of these, the child was not continuously looked after
    eps_copy['implies_not_continuous'] = (enters_care | leaves_care | V3_V4_episode)

    in_care_at_some_point = eps_copy.groupby('CHILD')['during_year'].transform('max')
    not_in_care_at_some_point = eps_copy.groupby('CHILD')['implies_not_continuous'].transform('max')

    # the "== True/False" is to cope with weird situations which cause these to potentially be float dtype,
    # which i don't have time to get into right now, but may be to do with missing DECOMs
    episodes['CONTINUOUSLY_LOOKED_AFTER'] = (in_care_at_some_point == True) & (not_in_care_at_some_point == False)

    return episodes


def add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER(dfs, required_tables=None):
    """
    Takes: the `dfs` dict and `required_tables` (table name or list of table names)
    Returns: The Dataframe or list of Dataframes named in `required_tables`,
             now with an additional column 'CONTINUOUSLY_LOOKED_AFTER'

    (NB: currently modifies, and returns references to, the original DataFrames in `dfs`)
    """
    CLA_col = 'CONTINUOUSLY_LOOKED_AFTER'
    try:
        metadata = dfs['metadata']
        eps = dfs['Episodes']
    except KeyError:
        raise KeyError(f"Ensure 'Episodes' and 'metadata' in `dfs` before attempting to determine "
                       + f"CONTINUOUSLY_LOOKED_AFTER -- only received: {', '.join(str(i) for i in dfs.keys())}")

    eps_with_CLA = add_col_to_episodes_CONTINUOUSLY_LOOKED_AFTER(eps, metadata['collection_start'], metadata['collection_end'])
    known_CLA = eps_with_CLA.drop_duplicates('CHILD')

    if isinstance(required_tables, str):
        required_tables = [required_tables, ]
        return_df_not_list = True
    else:
        return_df_not_list = False

    if len(set(required_tables) - set(dfs.keys())) > 0:
        raise KeyError("required_tables should be a key, or a collection of keys, of the dfs dict")
    elif 'metadata' in required_tables:
        raise ValueError("cannot add CONTINUOUSLY_LOOKED_AFTER to 'metadata'")

    else:
        out = []
        for table_name in required_tables:
            if table_name == 'Episodes':
                df = eps_with_CLA
            else:
                df = dfs[table_name]
                merged = pd.merge(left=df['CHILD'], right=known_CLA, on='CHILD', how='left')
                df[CLA_col] = merged[CLA_col]
                df[CLA_col].fillna(False, inplace=True)
            out.append(df)
    if return_df_not_list and len(out) == 1:
        return out[0]
    else:
        return out
