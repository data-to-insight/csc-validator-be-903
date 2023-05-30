import pandas as pd

def decom_before_dob(dfs, p_code, y_gap):
    epi = dfs['Episodes']
    hea = dfs['Header']

    epi.reset_index(inplace=True)
    epi_p2 = epi[epi['PLACE'] == p_code]
    merged_e = epi_p2.merge(hea, how='inner', on='CHILD')
    merged_e = merged_e.dropna(subset=['DECOM', 'DEC', 'DOB'])
    # if subval in ['370', '371', '372', '373', '374']:
    error_mask = merged_e['DECOM'] < (merged_e['DOB'] +
                                        pd.offsets.DateOffset(years=y_gap))
    # else:
    #     error_mask = merged_e['DEC'] > (merged_e['DECOM'] +
    #                                     pd.offsets.DateOffset(days=y_gap))
    return {'Episodes': merged_e['index'][error_mask].unique().tolist()}

def dec_after_decom(dfs, p_code, y_gap):
    epi = dfs['Episodes']
    hea = dfs['Header']
    
    epi.reset_index(inplace=True)
    epi_p2 = epi[epi['PLACE'] == p_code]
    merged_e = epi_p2.merge(hea, how='inner', on='CHILD')
    merged_e = merged_e.dropna(subset=['DECOM', 'DEC', 'DOB'])
    # if subval in ['370', '371', '372', '373', '374']:
    #     error_mask = merged_e['DECOM'] < (merged_e['DOB'] +
    #                                         pd.offsets.DateOffset(years=y_gap))
    # else:
    error_mask = merged_e['DEC'] > (merged_e['DECOM'] +
                                    pd.offsets.DateOffset(days=y_gap))
    return {'Episodes': merged_e['index'][error_mask].unique().tolist()}