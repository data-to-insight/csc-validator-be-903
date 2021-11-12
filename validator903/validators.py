import pandas as pd
from .types import ErrorDefinition

def validate_516():
    error = ErrorDefinition(
        code = '516',
        description = 'The episode data submitted for this child does not show that he/she was with their former foster carer(s) during the year.If the code in the reason episode ceased is E45 or E46 the child must have a placement code of U1 to U6.',
        affected_fields=['REC','PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
          return{}

        else:
            episodes = dfs['Episodes']
            bad_place_codes = ['A3','A4','A5','A6','H5','K1','K2', 'P1', 'P2', 'P3', 'R1', 'R2', 'R3', 'R5', 'S1', 'T0', 'T1', 'T2', 'T3', 'T4', 'Z1']
            rec_codes = ['E45','E46']


            mask = episodes['REC'].isin(rec_codes) & episodes['PLACE'].isin(bad_place_codes)

            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return{'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_452():
    error = ErrorDefinition(
        code = '452',
        description = 'Contradiction between local authority of placement code in the last episode of the previous year and in the first episode of the current year.',
        affected_fields=['PL_POST'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
          return {}
        if 'Episodes_last' not in dfs:
          return {}
        else:
            episodes = dfs['Episodes']
            episodes_last = dfs['Episodes_last']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'],format='%d/%m/%Y',errors='coerce')
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'],format='%d/%m/%Y',errors='coerce')

            episodes_min = episodes.groupby('CHILD')['DECOM'].idxmin()
            episodes_last_max = episodes_last.groupby('CHILD')['DECOM'].idxmax()

            episodes = episodes[episodes.index.isin(episodes_min)]
            episodes_last = episodes_last[episodes_last.index.isin(episodes_last_max)]

            episodes_merged = episodes.reset_index().merge(episodes_last, how='left', on=['CHILD'], suffixes=('','_last'), indicator=True).set_index('index')

            in_both_years = episodes_merged['_merge'] == 'both'
            same_rne = episodes_merged['RNE'] == episodes_merged['RNE_last']
            last_year_open = episodes_merged['DEC_last'].isna()
            different_pl_la = episodes_merged['PL_LA'] != episodes_merged['PL_LA_last']

            error_mask = in_both_years & same_rne & last_year_open & different_pl_la

            validation_error_locations = episodes.index[error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_386():
    error = ErrorDefinition(
        code = '386',
        description = 'Reason episode ceased is adopted but child has reached age 18.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'],format='%d/%m/%Y',errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'],format='%d/%m/%Y',errors='coerce')
            header['DOB18'] = header['DOB'] + pd.DateOffset(years=18)

            episodes_merged = (
                episodes
                    .reset_index()
                    .merge(header, how='left', on=['CHILD'], suffixes=('', '_header'), indicator=True)
                    .set_index('index')
                    .dropna(subset=['DOB18', 'DEC'])
            )

            ceased_adopted = episodes_merged['REC'].str.upper().astype(str).isin(['E11','E12'])
            ceased_under_18 = episodes_merged['DOB18'] > episodes_merged['DEC']

            error_mask = ceased_adopted & ~ceased_under_18

            error_locations = episodes_merged.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate

def validate_363():
    error = ErrorDefinition(
        code = '363',
        description = 'Child assessment order (CAO) lasted longer than 7 days allowed in the Children Act 1989.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        episodes = dfs['Episodes']
        collection_end_str = dfs['metadata']['collection_end']

        L2_eps = episodes[episodes['LS'] == 'L2'].copy()
        L2_eps['original_index'] = L2_eps.index
        L2_eps = L2_eps[L2_eps['DECOM'].notna()]

        L2_eps.loc[L2_eps['DEC'].isna(), 'DEC'] = collection_end_str
        L2_eps['DECOM'] = pd.to_datetime(L2_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
        L2_eps = L2_eps.dropna(subset=['DECOM'])
        L2_eps['DEC'] = pd.to_datetime(L2_eps['DEC'], format='%d/%m/%Y', errors='coerce')

        L2_eps.sort_values(['CHILD', 'DECOM'])

        L2_eps['index'] = pd.RangeIndex(0, len(L2_eps))
        L2_eps['index+1'] = L2_eps['index'] + 1
        L2_eps = L2_eps.merge(L2_eps, left_on='index', right_on='index+1',
                              how='left', suffixes=[None, '_prev'])
        L2_eps = L2_eps[['original_index', 'DECOM', 'DEC', 'DEC_prev', 'CHILD', 'CHILD_prev', 'LS']]

        L2_eps['new_period'] = (
            (L2_eps['DECOM'] > L2_eps['DEC_prev'])
            | (L2_eps['CHILD'] != L2_eps['CHILD_prev'])
        )

        L2_eps['duration'] = (L2_eps['DEC'] - L2_eps['DECOM']).dt.days
        L2_eps['period_id'] = L2_eps['new_period'].astype(int).cumsum()
        L2_eps['period_duration'] = L2_eps.groupby('period_id')['duration'].transform(sum)

        error_mask = L2_eps['period_duration'] > 7

        return {'Episodes': L2_eps.loc[error_mask, 'original_index'].to_list()}

    return error, _validate


def validate_364():
    error = ErrorDefinition(
        code = '364',
        description = 'Sections 41-46 of Police and Criminal Evidence (PACE; 1984) severely limits ' +
                      'the time a child can be detained in custody in Local Authority (LA) accommodation.',
        affected_fields=['LS','DECOM','DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        episodes = dfs['Episodes']
        collection_end_str = dfs['metadata']['collection_end']

        J2_eps = episodes[episodes['LS'] == 'J2'].copy()
        J2_eps['original_index'] = J2_eps.index

        J2_eps['DECOM'] = pd.to_datetime(J2_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
        J2_eps = J2_eps[J2_eps['DECOM'].notna()]
        J2_eps.loc[J2_eps['DEC'].isna(), 'DEC'] = collection_end_str
        J2_eps['DEC'] = pd.to_datetime(J2_eps['DEC'], format='%d/%m/%Y', errors='coerce')

        J2_eps.sort_values(['CHILD', 'DECOM'])

        J2_eps['index'] = pd.RangeIndex(0, len(J2_eps))
        J2_eps['index_prev'] = J2_eps['index'] + 1
        J2_eps = J2_eps.merge(J2_eps, left_on='index', right_on='index_prev',
                              how='left', suffixes=[None, '_prev'])
        J2_eps = J2_eps[['original_index', 'DECOM', 'DEC', 'DEC_prev', 'CHILD', 'CHILD_prev', 'LS']]

        J2_eps['new_period'] = (
            (J2_eps['DECOM'] > J2_eps['DEC_prev'])
            | (J2_eps['CHILD'] != J2_eps['CHILD_prev'])
        )

        J2_eps['duration'] = (J2_eps['DEC'] - J2_eps['DECOM']).dt.days
        J2_eps['period_id'] = J2_eps['new_period'].astype(int).cumsum()
        J2_eps['period_duration'] = J2_eps.groupby('period_id')['duration'].transform(sum)

        error_mask = J2_eps['period_duration'] > 21

        return {'Episodes': J2_eps.loc[error_mask, 'original_index'].to_list()}

    return error, _validate


def validate_365():
    error = ErrorDefinition(
        code = '365',
        description = 'Any individual short- term respite placement must not exceed 17 days.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        episodes = dfs['Episodes']
        collection_end_str = dfs['metadata']['collection_end']

        episodes.loc[episodes['DEC'].isna(), 'DEC'] = collection_end_str
        episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
        episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

        over_17_days = episodes['DEC'] > episodes['DECOM'] + pd.DateOffset(days=17)
        error_mask = (episodes['LS'] == 'V2') & over_17_days

        return {'Episodes': episodes.index[error_mask].to_list()}

    return error, _validate


def validate_367():
    error = ErrorDefinition(
        code = '367',
        description = 'The maximum amount of respite care allowable is 75 days in any 12-month period.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        V3_eps = episodes[episodes['LS'] == 'V3']

        V3_eps = V3_eps.dropna(subset=['DECOM']) # missing DECOM should get fixed before looking for this error

        collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
        V3_eps['DECOM_dt'] = pd.to_datetime(V3_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
        V3_eps['DEC_dt'] = pd.to_datetime(V3_eps['DEC'], format='%d/%m/%Y', errors='coerce')

        # truncate episode start/end dates to collection start/end respectively
        V3_eps.loc[V3_eps['DEC'].isna() | (V3_eps['DEC_dt'] > collection_end), 'DEC_dt'] = collection_end
        V3_eps.loc[V3_eps['DECOM_dt'] < collection_start, 'DECOM_dt'] = collection_start

        V3_eps['duration'] = (V3_eps['DEC_dt'] - V3_eps['DECOM_dt']).dt.days
        V3_eps = V3_eps[V3_eps['duration'] > 0]

        V3_eps['year_total_duration'] = V3_eps.groupby('CHILD')['duration'].transform(sum)

        error_mask = V3_eps['year_total_duration'] > 75

        return {'Episodes': V3_eps.index[error_mask].to_list()}

    return error, _validate


def validate_440():
    error = ErrorDefinition(
        code = '440',
        description = 'Participation method indicates child was under 4 years old at the time of the review, but date of birth and review date indicates the child was 4 years old or over.',
        affected_fields=['DOB','REVIEW','REVIEW_CODE'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
          return {}
        else:
            reviews = dfs['Reviews']
            reviews['DOB'] = pd.to_datetime(reviews['DOB'],format='%d/%m/%Y',errors='coerce')
            reviews['REVIEW'] = pd.to_datetime(reviews['REVIEW'],format='%d/%m/%Y',errors='coerce')

            mask = reviews['REVIEW_CODE'].eq('PN0') & (reviews['REVIEW'] > reviews['DOB'] + pd.offsets.DateOffset(years=4))

            validation_error_mask = mask
            validation_error_locations = reviews.index[validation_error_mask]

            return {'Reviews': validation_error_locations.tolist()}

    return error, _validate

def validate_445():
    error = ErrorDefinition(
        code = '445',
        description = 'D1 is not a valid code for episodes starting after December 2005.',
        affected_fields=['LS','DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
          return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'],format='%d/%m/%Y',errors='coerce')
            max_decom_allowed = pd.to_datetime('31/12/2005', format='%d/%m/%Y', errors='coerce')

            mask = episodes['LS'].eq('D1') & (episodes['DECOM'] > max_decom_allowed)
            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_446():
    error = ErrorDefinition(
        code = '446',
        description = 'E1 is not a valid code for episodes starting before December 2005.',
        affected_fields=['LS','DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
          return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'],format='%d/%m/%Y',errors='coerce')
            min_decom_allowed = pd.to_datetime('01/12/2005', format='%d/%m/%Y', errors='coerce')

            mask = episodes['LS'].eq('E1') & (episodes['DECOM'] < min_decom_allowed)
            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_208():
    error = ErrorDefinition(
        code = '208',
        description = 'Unique Pupil Number (UPN) for the current year disagrees with the Unique Pupil Number (UPN) already recorded for this child.',
        affected_fields=['UPN'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            upn_is_different = header_merged['UPN'].str.upper().astype(str) != header_merged['UPN_last'].str.upper().astype(str)
            upn_not_recorded = header_merged['UPN'].str.upper().astype(str).isin(['UN2','UN3','UN4','UN5','UN6']) & header_merged['UPN_last'].str.upper().astype(str).isin(['UN1'])

            error_mask = in_both_years & upn_is_different & ~upn_not_recorded

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate

def validate_204():
    error = ErrorDefinition(
        code = '204',
        description = 'Ethnic origin code disagrees with the ethnic origin already recorded for this child.',
        affected_fields=['ETHNIC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            ethnic_is_different = header_merged['ETHNIC'].astype(str).str.upper() != header_merged['ETHNIC_last'].astype(str).str.upper()

            error_mask = in_both_years & ethnic_is_different

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate

def validate_203():
    error = ErrorDefinition(
        code = '203',
        description = 'Date of birth disagrees with the date of birth already recorded for this child.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header['DOB'] = pd.to_datetime(header['DOB'],format='%d/%m/%Y',errors='coerce')
            header_last['DOB'] = pd.to_datetime(header_last['DOB'],format='%d/%m/%Y',errors='coerce')

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            dob_is_different = header_merged['DOB'].astype(str) != header_merged['DOB_last'].astype(str)

            error_mask = in_both_years & dob_is_different

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate

def validate_530():
    error = ErrorDefinition(
          code = '530',
          description = "A placement provider code of PR4 cannot be associated with placement P1.",
          affected_fields=['PLACE', 'PLACE_PROVIDER'],
      )
    def _validate(dfs):
        if 'Episodes' not in dfs:
          return {}
        else:
            episodes = dfs['Episodes']
            mask = episodes['PLACE'].eq('P1') & episodes['PLACE_PROVIDER'].eq('PR4')

            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_571():
    error = ErrorDefinition(
        code = '571',
        description = 'The date that the child ceased to be missing or away from placement without authorisation is before the start or after the end of the collection year.',
        affected_fields=['MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'],format='%d/%m/%Y',errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'],format='%d/%m/%Y',errors='coerce')

            missing['fMIS_END'] = pd.to_datetime(missing['MIS_END'], format='%d/%m/%Y', errors='coerce')

            end_date_before_year = missing['fMIS_END'] < collection_start
            end_date_after_year = missing['fMIS_END'] > collection_end

            error_mask = end_date_before_year | end_date_after_year

            error_locations = missing.index[error_mask]

            return {'Missing': error_locations.to_list()}

    return error, _validate

def validate_1005():
    error = ErrorDefinition(
        code = '1005',
        description = 'The end date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.',
        affected_fields=['MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']
            missing['fMIS_END'] = pd.to_datetime(missing['MIS_END'], format='%d/%m/%Y', errors='coerce')

            missing_end_date = missing['MIS_END'].isna()
            invalid_end_date = missing['fMIS_END'].isna()

            error_mask = ~missing_end_date & invalid_end_date

            error_locations = missing.index[error_mask]

            return {'Missing': error_locations.to_list()}

    return error, _validate

def validate_1004():
    error = ErrorDefinition(
        code = '1004',
        description = 'The start date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.',
        affected_fields=['MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']

            missing['fMIS_START'] = pd.to_datetime(missing['MIS_START'], format='%d/%m/%Y', errors='coerce')

            missing_start_date = missing['MIS_START'].isna()
            invalid_start_date = missing['fMIS_START'].isna()

            error_mask = missing_start_date | invalid_start_date

            error_locations = missing.index[error_mask]

            return {'Missing': error_locations.to_list()}
    return error, _validate

def validate_202():
    error = ErrorDefinition(
        code = '202',
        description = 'The gender code conflicts with the gender already recorded for this child.',
        affected_fields=['SEX'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            sex_is_different = header_merged['SEX'].astype(str) != header_merged['SEX_last'].astype(str)

            error_mask = in_both_years & sex_is_different

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate

def validate_621():
    error = ErrorDefinition(
        code = '621',
        description = "Mother’s field has been completed but date of birth shows that the mother is younger than her child.",
        affected_fields=['DOB', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            header['MC_DOB'] = pd.to_datetime(header['MC_DOB'],format='%d/%m/%Y',errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'],format='%d/%m/%Y',errors='coerce')

            mask = (header['MC_DOB'] > header['DOB']) | header['MC_DOB'].isna()

            validation_error_mask = ~mask
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}
    return error, _validate

def validate_556():
    error = ErrorDefinition(
        code = '556',
        description = 'Date of decision that the child should be placed for adoption should be on or prior to the date that the freeing order was granted.',
        affected_fields=['DATE_PLACED', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placedAdoptions = dfs['PlacedAdoption']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'],format='%d/%m/%Y',errors='coerce')
            placedAdoptions['DATE_PLACED'] = pd.to_datetime(placedAdoptions['DATE_PLACED'],format='%d/%m/%Y',errors='coerce')

            episodes = episodes.reset_index()

            D1Episodes = episodes[episodes['LS'] == 'D1']

            merged = D1Episodes.reset_index().merge(placedAdoptions, how='left', on='CHILD',).set_index('index')

            episodes_with_errors = merged[merged['DATE_PLACED'] > merged['DECOM']]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_393():
    error = ErrorDefinition(
        code = '393',
        description = 'Child is looked after but mother field is not completed.',
        affected_fields = ['MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header_female = header[header['SEX'].astype(str) == '2']

            applicable_episodes = episodes[~episodes['LS'].str.upper().isin(['V3','V4'])]

            error_mask = header_female['CHILD'].isin(applicable_episodes['CHILD']) & header_female['MOTHER'].isna()

            error_locations = header_female.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate

def validate_NoE():
    error = ErrorDefinition(
        code = 'NoE',
        description = 'This child has no episodes loaded for previous year even though child started to be looked after before this current year.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'],format='%d/%m/%Y',errors='coerce')
            episodes_last = dfs['Episodes_last']
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'],format='%d/%m/%Y',errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'],format='%d/%m/%Y',errors='coerce')

            episodes_before_year = episodes[episodes['DECOM'] < collection_start]

            episodes_merged = episodes_before_year.reset_index().merge(episodes_last, how='left', on=['CHILD'], indicator=True).set_index('index')

            episodes_not_matched = episodes_merged[episodes_merged['_merge'] == 'left_only']
            
            error_mask = episodes.index.isin(episodes_not_matched.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate

def validate_356():
    error = ErrorDefinition(
        code = '356',
        description = 'The date the episode ceased is before the date the same episode started.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'],format='%d/%m/%Y',errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'],format='%d/%m/%Y',errors='coerce')

            error_mask = episodes['DEC'].notna() &(episodes['DEC'] < episodes['DECOM'])
          
            return {'Episodes': episodes.index[error_mask].to_list()}

    return error, _validate

def validate_611():
    error = ErrorDefinition(
        code = '611',
        description = "Date of birth field is blank, but child is a mother.",
        affected_fields=['MOTHER', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            validation_error_mask = header['MOTHER'].astype(str).isin(['1']) & header['MC_DOB'].isna()
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}
    
    return error, _validate

def validate_1009():
    error = ErrorDefinition(
        code='1009',
        description='Reason for placement change is not a valid code.',
        affected_fields=['REASON_PLACE_CHANGE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        
        episodes = dfs['Episodes']
        code_list = [
          'CARPL', 
          'CLOSE', 
          'ALLEG', 
          'STAND',
          'APPRR', 
          'CREQB', 
          'CREQO', 
          'CHILD',
          'LAREQ', 
          'PLACE', 
          'CUSTOD', 
          'OTHER'
        ]

        mask = episodes['REASON_PLACE_CHANGE'].isin(code_list) | episodes['REASON_PLACE_CHANGE'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_1006():
    error = ErrorDefinition(
        code='1006',
        description='Missing type invalid.',
        affected_fields=['MISSING'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        
        missing_from_care = dfs['Missing']
        code_list = ['M', 'A']

        mask = missing_from_care['MISSING'].isin(code_list) | missing_from_care['MISSING'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = missing_from_care.index[validation_error_mask]

        return {'Missing': validation_error_locations.tolist()}

    return error, _validate

def validate_631():
    error = ErrorDefinition(
        code='631',
        description='Previous permanence option not a valid value.',
        affected_fields=['PREV_PERM'],
    )

    def _validate(dfs):
        if 'PrevPerm' not in dfs:
            return {}
        
        previous_permanence = dfs['PrevPerm']
        code_list = ['P1', 'P2', 'P3', 'P4', 'Z1']

        mask = previous_permanence['PREV_PERM'].isin(code_list) | previous_permanence['PREV_PERM'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = previous_permanence.index[validation_error_mask]

        return {'PrevPerm': validation_error_locations.tolist()}

    return error, _validate

def validate_196():
    error = ErrorDefinition(
        code='196',
        description='Strengths and Difficulties (SDQ) reason is not a valid code.',
        affected_fields=['SDQ_REASON'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        
        oc2 = dfs['OC2']
        code_list = ['SDQ1', 'SDQ2', 'SDQ3', 'SDQ4', 'SDQ5']

        mask = oc2['SDQ_REASON'].isin(code_list) | oc2['SDQ_REASON'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = oc2.index[validation_error_mask]

        return {'OC2': validation_error_locations.tolist()}

    return error, _validate

def validate_177():
    error = ErrorDefinition(
        code='177',
        description='The legal status of adopter(s) code is not a valid code.',
        affected_fields=['LS_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        
        adoptions = dfs['AD1']
        code_list = ['L0', 'L11', 'L12', 'L2', 'L3', 'L4']

        mask = adoptions['LS_ADOPTR'].isin(code_list) | adoptions['LS_ADOPTR'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate

def validate_176():
    error = ErrorDefinition(
        code='176',
        description='The gender of adopter(s) at the date of adoption code is not a valid code.',
        affected_fields=['SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        
        adoptions = dfs['AD1']
        code_list = ['M1', 'F1', 'MM', 'FF', 'MF']

        mask = adoptions['SEX_ADOPTR'].isin(code_list) | adoptions['SEX_ADOPTR'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate

def validate_175():
    error = ErrorDefinition(
        code='175',
        description='The number of adopter(s) code is not a valid code.',
        affected_fields=['NB_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        
        adoptions = dfs['AD1']
        code_list = ['1', '2']

        mask = adoptions['NB_ADOPTR'].astype(str).isin(code_list) | adoptions['NB_ADOPTR'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate

def validate_132():
    error = ErrorDefinition(
        code='132',
        description='Data entry for activity after leaving care is invalid.',
        affected_fields=['ACTIV'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        
        care_leavers = dfs['OC3']
        code_list = [
          'F1', 
          'P1', 
          'F2', 
          'P2', 
          'F3', 
          'P3', 
          'G4',
          'G5', 
          'G6', 
          '0'
          ]
        mask = care_leavers['ACTIV'].astype(str).isin(code_list) | care_leavers['ACTIV'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = care_leavers.index[validation_error_mask]

        return {'OC3': validation_error_locations.tolist()}

    return error, _validate

def validate_131():
    error = ErrorDefinition(
        code='131',
        description='Data entry for being in touch after leaving care is invalid.',
        affected_fields=['IN_TOUCH'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        
        care_leavers = dfs['OC3']
        code_list = [
          'YES', 
          'NO', 
          'DIED', 
          'REFU', 
          'NREQ', 
          'RHOM'
          ]
        mask = care_leavers['IN_TOUCH'].isin(code_list) | care_leavers['IN_TOUCH'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = care_leavers.index[validation_error_mask]

        return {'OC3': validation_error_locations.tolist()}

    return error, _validate

def validate_120():
    error = ErrorDefinition(
        code='120',
        description='The reason for the reversal of the decision that the child should be placed for adoption code is not valid.',
        affected_fields=['REASON_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        
        placed_adoptions = dfs['PlacedAdoption']
        code_list = ['RD1', 'RD2', 'RD3', 'RD4']

        mask = placed_adoptions['REASON_PLACED_CEASED'].isin(code_list) | placed_adoptions['REASON_PLACED_CEASED'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = placed_adoptions.index[validation_error_mask]

        return {'PlacedAdoption': validation_error_locations.tolist()}

    return error, _validate

def validate_114():
    error = ErrorDefinition(
        code='114',
        description='Data entry to record the status of former carer(s) of an adopted child is invalid.',
        affected_fields=['FOSTER_CARE'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        
        adoptions = dfs['AD1']
        code_list = ['0', '1']

        mask = adoptions['FOSTER_CARE'].astype(str).isin(code_list) | adoptions['FOSTER_CARE'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = adoptions.index[validation_error_mask]

        return {'AD1': validation_error_locations.tolist()}

    return error, _validate

def validate_178():
    error = ErrorDefinition(
        code='178',
        description='Placement provider code is not a valid code.',
        affected_fields=['PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        
        episodes = dfs['Episodes']
        
        code_list_placement_provider = ['PR0', 'PR1', 'PR2', 'PR3', 'PR4', 'PR5']
        code_list_placement_with_no_provider = ['T0', 'T1', 'T2', 'T3', 'T4', 'Z1']

        place_provider_needed_and_correct = episodes['PLACE_PROVIDER'].isin(code_list_placement_provider) & ~episodes['PLACE'].isin(code_list_placement_with_no_provider) 
        
        place_provider_not_provided = episodes['PLACE_PROVIDER'].isna() 
        
        place_provider_not_needed = episodes['PLACE_PROVIDER'].isna() & episodes['PLACE'].isin(code_list_placement_with_no_provider) 
        
        mask = place_provider_needed_and_correct | place_provider_not_provided | place_provider_not_needed

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_103():
    error = ErrorDefinition(
        code='103',
        description='The ethnicity code is either not valid or has not been entered.',
        affected_fields=['ETHNIC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        
        header = dfs['Header']
        code_list = [
          'WBRI', 
          'WIRI', 
          'WOTH', 
          'WIRT', 
          'WROM', 
          'MWBC', 
          'MWBA', 
          'MWAS', 
          'MOTH', 
          'AIND', 
          'APKN', 
          'ABAN', 
          'AOTH', 
          'BCRB', 
          'BAFR', 
          'BOTH', 
          'CHNE', 
          'OOTH', 
          'REFU', 
          'NOBT'
        ]

        mask = header['ETHNIC'].isin(code_list)

        validation_error_mask = ~mask
        validation_error_locations = header.index[validation_error_mask]

        return {'Header': validation_error_locations.tolist()}

    return error, _validate

def validate_143():
    error = ErrorDefinition(
        code='143',
        description='The reason for new episode code is not a valid code.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        
        episodes = dfs['Episodes']
        code_list = ['S', 'P', 'L', 'T', 'U', 'B']

        mask = episodes['RNE'].isin(code_list) | episodes['RNE'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_144():
    error = ErrorDefinition(
        code='144',
        description='The legal status code is not a valid code.',
        affected_fields=['LS'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        
        episodes = dfs['Episodes']
        code_list = [
          'C1', 
          'C2',
          'D1', 
          'E1', 
          'V2', 
          'V3', 
          'V4', 
          'J1', 
          'J2', 
          'J3', 
          'L1', 
          'L2',
          'L3'
        ]

        mask = episodes['LS'].isin(code_list) | episodes['LS'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_145():
    error = ErrorDefinition(
        code='145',
        description='Category of need code is not a valid code.',
        affected_fields=['CIN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        
        episodes = dfs['Episodes']
        code_list = [
          'N1', 
          'N2', 
          'N3', 
          'N4', 
          'N5', 
          'N6', 
          'N7', 
          'N8', 
        ]

        mask = episodes['CIN'].isin(code_list) | episodes['CIN'].isna()
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate
 
def validate_146():
    error = ErrorDefinition(
        code='146',
        description='Placement type code is not a valid code.',
        affected_fields=['PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        
        episodes = dfs['Episodes']
        code_list = [
          'A3', 
          'A4',
          'A5',
          'A6', 
          'H5', 
          'K1', 
          'K2', 
          'P1', 
          'P2', 
          'P3', 
          'R1', 
          'R2', 
          'R3', 
          'R5', 
          'S1', 
          'T0', 
          'T1', 
          'T2', 
          'T3', 
          'T4', 
          'U1', 
          'U2', 
          'U3', 
          'U4', 
          'U5', 
          'U6', 
          'Z1'
        ]

        mask = episodes['PLACE'].isin(code_list) | episodes['PLACE'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_149():
    error = ErrorDefinition(
        code='149',
        description='Reason episode ceased code is not valid. ',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        
        episodes = dfs['Episodes']
        code_list = [
          'E11',
          'E12', 
          'E2', 
          'E3', 
          'E4A', 
          'E4B', 
          'E13', 
          'E41',
          'E45', 
          'E46', 
          'E47', 
          'E48', 
          'E5', 
          'E6', 
          'E7', 
          'E8',
          'E9',
          'E14', 
          'E15',
          'E16', 
          'E17', 
          'X1'
        ]

        mask = episodes['REC'].isin(code_list) | episodes['REC'].isna()
        
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {'Episodes': validation_error_locations.tolist()}

    return error, _validate

def validate_167():
    error = ErrorDefinition(
        code='167',
        description='Data entry for participation is invalid or blank.',
        affected_fields=['REVIEW_CODE'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}
        
        review = dfs['Reviews']
        code_list = ['PN0', 'PN1', 'PN2', 'PN3', 'PN4', 'PN5', 'PN6', 'PN7']

        mask = review['REVIEW'].notna() & review['REVIEW_CODE'].isin(code_list) | review['REVIEW'].isna() & review['REVIEW_CODE'].isna()

        validation_error_mask = ~mask
        validation_error_locations = review.index[validation_error_mask]

        return {'Reviews': validation_error_locations.tolist()}
      
    return error, _validate 

def validate_101():
    error = ErrorDefinition(
        code='101',
        description='Gender code is not valid.',
        affected_fields=['SEX'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        
        header = dfs['Header']
        code_list = ['1', '2']

        mask = header['SEX'].astype(str).isin(code_list)

        validation_error_mask = ~mask
        validation_error_locations = header.index[validation_error_mask]

        return {'Header': validation_error_locations.tolist()}
      
    return error, _validate 

def validate_141():
    error = ErrorDefinition(
        code = '141',
        description = 'Date episode began is not a valid date.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = episodes['DECOM'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}
    
    return error, _validate

def validate_147():
    error = ErrorDefinition(
        code = '147',
        description = 'Date episode ceased is not a valid date.',
        affected_fields=['DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = episodes['DEC'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}
    
    return error, _validate

def validate_171():
    error = ErrorDefinition(
        code = '171',
        description = "Date of birth of mother's child is not a valid date.",
        affected_fields=['MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            mask = pd.to_datetime(header['MC_DOB'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = header['MC_DOB'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}
    
    return error, _validate

def validate_102():
    error = ErrorDefinition(
        code='102',
        description='Date of birth is not a valid date.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            mask = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce').notna()

            validation_error_mask = ~mask
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}
    
    return error, _validate

def validate_112():
    error = ErrorDefinition(
        code='112',
        description='Date should be placed for adoption is not a valid date.',
        affected_fields=['DATE_INT'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            mask = pd.to_datetime(ad1['DATE_INT'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = ad1['DATE_INT'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = ad1.index[validation_error_mask]

            return {'AD1': validation_error_locations.tolist()}
    
    return error, _validate

def validate_115():
    error = ErrorDefinition(
        code='115',
        description="Date of Local Authority's (LA) decision that a child should be placed for adoption is not a valid date.",
        affected_fields=['DATE_PLACED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            adopt = dfs['PlacedAdoption']
            mask = pd.to_datetime(adopt['DATE_PLACED'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = adopt['DATE_PLACED'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = adopt.index[validation_error_mask]

            return {'PlacedAdoption': validation_error_locations.tolist()}
    
    return error, _validate

def validate_116():
    error = ErrorDefinition(
        code='116',
        description="Date of Local Authority's (LA) decision that a child should no longer be placed for adoption is not a valid date.",
        affected_fields=['DATE_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            adopt = dfs['PlacedAdoption']
            mask = pd.to_datetime(adopt['DATE_PLACED_CEASED'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = adopt['DATE_PLACED_CEASED'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = adopt.index[validation_error_mask]

            return {'PlacedAdoption': validation_error_locations.tolist()}
    
    return error, _validate

def validate_392c():
    error = ErrorDefinition(
        code='392c',
        description='Postcode(s) provided are invalid.',
        affected_fields=['HOME_POST', 'PL_POST'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            if 'postcodes' not in dfs['metadata']:
                return {'Episodes': []}

            episodes = dfs['Episodes']
            postcode_list = set(dfs['metadata']['postcodes']['pcd'])

            is_valid = lambda x: str(x).replace(' ', '') in postcode_list
            home_provided = episodes['HOME_POST'].notna()
            home_valid = episodes['HOME_POST'].apply(is_valid)
            pl_provided = episodes['PL_POST'].notna()
            pl_valid = episodes['PL_POST'].apply(is_valid)

            error_mask = (home_provided & ~home_valid) | (pl_provided & ~pl_valid)

            return {'Episodes': episodes.index[error_mask].tolist()}

    return error, _validate

def validate_213():
    error = ErrorDefinition(
        code='213',
        description='Placement provider information not required.',
        affected_fields=['PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = df['PLACE'].isin(['T0','T1','T2','T3','T4','Z1']) & df['PLACE_PROVIDER'].notna()
            return {'Episodes': df.index[mask].tolist()}
    
    return error, _validate

def validate_168():
    error = ErrorDefinition(
        code='168',
        description='Unique Pupil Number (UPN) is not valid. If unknown, default codes should be UN1, UN2, UN3, UN4 or UN5.',
        affected_fields=['UPN'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            df = dfs['Header']
            mask = df['UPN'].str.match(r'(^((?![IOS])[A-Z]){1}(\d{12}|\d{11}[A-Z]{1})$)|^(UN[1-5])$',na=False)
            mask = ~mask
            return {'Header': df.index[mask].tolist()}
    
    return error, _validate

def validate_388():
    error = ErrorDefinition(
        code='388',
        description='Reason episode ceased is coded new episode begins, but there is no continuation episode.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            df['DECOM'] = pd.to_datetime(df['DECOM'], format='%d/%m/%Y', errors='coerce')
            df['DEC'] = pd.to_datetime(df['DEC'], format='%d/%m/%Y', errors='coerce')

            df['DECOM'] = df['DECOM'].fillna('01/01/1901') #Watch for potential future issues
            df = df.sort_values(['CHILD','DECOM'])

            df['DECOM_NEXT_EPISODE'] = df.groupby(['CHILD'])['DECOM'].shift(-1)

            grouped_decom_by_child = df.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)

            #Dataframe with the maximum DECOM removed
            max_decom_removed = df.loc[~df.index.isin(grouped_decom_by_child),:]
            #Dataframe with the maximum DECOM only
            max_decom_only= df.loc[df.index.isin(grouped_decom_by_child),:]

            #Case 1: If reason episode ceased is coded X1 there must be a subsequent episode 
            #        starting on the same day.
            case1 = max_decom_removed[(max_decom_removed['REC'] == 'X1') & 
                   (max_decom_removed['DEC'].notna()) & 
                   (max_decom_removed['DECOM_NEXT_EPISODE'].notna()) &
                   (max_decom_removed['DEC'] != max_decom_removed['DECOM_NEXT_EPISODE'])]

            #Case 2: If an episode ends but the child continues to be looked after, a new
            #        episode should start on the same day.The reason episode ceased code of
            #        the episode which ends must be X1.
            case2 = max_decom_removed[(max_decom_removed['REC'] != 'X1') & 
                   (max_decom_removed['REC'].notna()) & 
                   (max_decom_removed['DEC'].notna()) & 
                   (max_decom_removed['DECOM_NEXT_EPISODE'].notna()) &
                   (max_decom_removed['DEC'] == max_decom_removed['DECOM_NEXT_EPISODE'])]

            #Case 3: If a child ceases to be looked after reason episode ceased code X1 must
            #        not be used. 
            case3 = max_decom_only[(max_decom_only['DEC'].notna()) & 
                   (max_decom_only['REC'] == 'X1')]

            mask_case1 = case1.index.tolist()
            mask_case2 = case2.index.tolist()
            mask_case3 = case3.index.tolist()

            mask = mask_case1 + mask_case2 + mask_case3

            mask.sort()
            return {'Episodes': mask}
    
    return error, _validate

def validate_113():
    error = ErrorDefinition(
        code='113',
        description='Date matching child and adopter(s) is not a valid date.',
        affected_fields=['DATE_MATCH'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            mask = pd.to_datetime(ad1['DATE_MATCH'], format='%d/%m/%Y', errors='coerce').notna()

            na_location = ad1['DATE_MATCH'].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = ad1.index[validation_error_mask]
        

            return {'AD1': validation_error_locations.tolist()}
    
    return error, _validate

def validate_134():
    error = ErrorDefinition(
        code='134',
        description='Data on adoption should not be entered for the OC3 cohort.',
        affected_fields=['IN_TOUCH','ACTIV','ACCOM','DATE_INT','DATE_MATCH','FOSTER_CARE','NB_ADOPTR','SEX_ADOPTR','LS_ADOPTR'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            ad1 = dfs['AD1']

            all_data = ad1.merge(oc3, how='left', on='CHILD')

            na_oc3_data = (
              all_data['IN_TOUCH'].isna() &
              all_data['ACTIV'].isna() &
              all_data['ACCOM'].isna()
            )
            na_ad1_data = (
              all_data['DATE_INT'].isna() &
              all_data['DATE_MATCH'].isna() &
              all_data['FOSTER_CARE'].isna() &
              all_data['NB_ADOPTR'].isna() &
              all_data['SEX_ADOPTR'].isna() &
              all_data['LS_ADOPTR'].isna()
            )


            validation_error = ~na_oc3_data & ~na_ad1_data
            validation_error_locations = ad1.index[validation_error]
        

            return {'OC3': validation_error_locations.tolist()}
    
    return error, _validate

def validate_119():
    error = ErrorDefinition(
        code='119',
        description='If the decision is made that a child should no longer be placed for adoption, then the date of this decision and the reason why this decision was made must be completed.',
        affected_fields=['REASON_PLACED_CEASED','DATE_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            adopt = dfs['PlacedAdoption']
            na_placed_ceased = adopt['DATE_PLACED_CEASED'].isna()
            na_reason_ceased = adopt['REASON_PLACED_CEASED'].isna()

            validation_error = (na_placed_ceased & ~na_reason_ceased) | (~na_placed_ceased & na_reason_ceased) 
            validation_error_locations = adopt.index[validation_error]
        

            return {'PlacedAdoption': validation_error_locations.tolist()}
    
    return error, _validate

def validate_142():
    error = ErrorDefinition(
        code='142',
        description='A new episode has started, but the previous episode has not ended.',
        affected_fields=['DEC','REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            df['DECOM'] = pd.to_datetime(df['DECOM'], format='%d/%m/%Y', errors='coerce')
            df['DEC'] = pd.to_datetime(df['DEC'], format='%d/%m/%Y', errors='coerce')

            df['DECOM'] = df['DECOM'].fillna('01/01/1901') #Watch for potential future issues

            index_of_last_episodes = df.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            df['DECOM'] = df['DECOM'].replace('01/01/1901',pd.NA)

            ended_episodes_df = df.loc[~df.index.isin(index_of_last_episodes),:]

            ended_episodes_df = ended_episodes_df[(ended_episodes_df['DEC'].isna() | ended_episodes_df['REC'].isna()) & 
                                ended_episodes_df['CHILD'].notna() & ended_episodes_df['DECOM'].notna()]
            mask = ended_episodes_df.index.tolist()

            return{'Episodes': mask}
    
    return error, _validate

def validate_148():
    error = ErrorDefinition(
        code='148',
        description='Date episode ceased and reason episode ceased must both be coded, or both left blank.',
        affected_fields=['DEC','REC'],
    )
    
    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            df['DEC'] = pd.to_datetime(df['DEC'], format='%d/%m/%Y', errors='coerce')

            mask = ((df['DEC'].isna()) & (df['REC'].notna())) | ((df['DEC'].notna()) & (df['REC'].isna()))

            return{'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_151():
    error = ErrorDefinition(
       code='151',
       description='All data items relating to a childs adoption must be coded or left blank.',
       affected_fields=['DATE_INT','DATE_MATCH','FOSTER_CARE','NB_ADOPTER','SEX_ADOPTR','LS_ADOPTR'],
    )
    def _validate(dfs):
        if 'AD1' not in dfs:
           return {}
        else:
           ad1 = dfs['AD1']
           na_date_int = ad1['DATE_INT'].isna()
           na_date_match = ad1['DATE_MATCH'].isna()
           na_foster_care = ad1['FOSTER_CARE'].isna()
           na_nb_adoptr = ad1['NB_ADOPTR'].isna()
           na_sex_adoptr = ad1['SEX_ADOPTR'].isna()
           na_lsadoptr = ad1['LS_ADOPTR'].isna()

           ad1_not_null = (~na_date_int & ~na_date_match &  ~na_foster_care & ~na_nb_adoptr& ~na_sex_adoptr & ~na_lsadoptr)

           validation_error = (~na_date_int | ~na_date_match | ~na_foster_care | ~na_nb_adoptr | ~na_sex_adoptr |~na_lsadoptr) & ~ad1_not_null
           validation_error_locations = ad1.index[validation_error]

           return {'AD1': validation_error_locations.tolist()}

    return error,_validate

def validate_182():
    error = ErrorDefinition(
        code='182',
        description='Data entries on immunisations, teeth checks, health assessments and substance misuse problem identified should be completed or all OC2 fields should be left blank.',
        affected_fields=['IMMUNISATIONS','TEETH_CHECK','HEALTH_ASSESSMENT','SUBSTANCE_MISUSE','CONVICTED','HEALTH_CHECK','INTERVENTION_RECEIVED','INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            mask1 = (
              oc2['IMMUNISATIONS'].isna() |
              oc2['TEETH_CHECK'].isna() |
              oc2['HEALTH_ASSESSMENT'].isna() |
              oc2['SUBSTANCE_MISUSE'].isna()
            )
            mask2 = (
              oc2['CONVICTED'].isna() &
              oc2['HEALTH_CHECK'].isna() &
              oc2['INTERVENTION_RECEIVED'].isna() &
              oc2['INTERVENTION_OFFERED'].isna()
            )


            validation_error = mask1 & ~mask2
            validation_error_locations = oc2.index[validation_error]
        

            return {'OC2': validation_error_locations.tolist()}
        
    return error, _validate

def validate_214():
    error = ErrorDefinition(
        code='214',
        description='Placement location information not required.',
        affected_fields=['PL_POST','URN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = df['LS'].isin(['V3','V4']) & ((df['PL_POST'].notna()) | (df['URN'].notna()))
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_222():
    error = ErrorDefinition(
        code='222',
        description='Ofsted Unique reference number (URN) should not be recorded for this placement type.',
        affected_fields=['URN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            place_code_list = ['H5','P1','P2','P3','R1','R2','R5','T0','T1','T2','T3','T4','Z1']
            mask = (df['PLACE'].isin(place_code_list)) & (df['URN'].notna()) & (df['URN'] != 'XXXXXX')
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_366():
    error = ErrorDefinition(
        code='366',
        description='A child cannot change placement during the course of an individual short-term respite break.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = (df['LS'] == 'V3') & (df['RNE'] != 'S')
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_628():
    error = ErrorDefinition(
        code='628',
        description='Motherhood details are not required for care leavers who have not been looked after during the year.',
        affected_fields=['MOTHER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            hea = dfs['Header']
            epi = dfs['Episodes']
            oc3 = dfs['OC3']
            
            hea = hea.reset_index()
            oc3_no_nulls = oc3[oc3[['IN_TOUCH','ACTIV','ACCOM']].notna().any(axis=1)]

            hea_merge_epi = hea.merge(epi,how='left',on='CHILD',indicator=True)
            hea_not_in_epi = hea_merge_epi[hea_merge_epi['_merge'] == 'left_only']

            cohort_to_check = hea_not_in_epi.merge(oc3_no_nulls,how='inner',on='CHILD')
            error_cohort = cohort_to_check[cohort_to_check['MOTHER'].notna()]
            
            error_list = list(set(error_cohort['index'].to_list()))
            error_list.sort()
            return {'Header': error_list}

    return error, _validate

def validate_164():
    error = ErrorDefinition(
        code='164',
        description='Distance is not valid. Please check a valid postcode has been entered.',
        affected_fields=['PL_DISTANCE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])
            distance = pd.to_numeric(df['PL_DISTANCE'], errors='coerce')
            # Use a bit of tolerance in these bounds
            distance_valid = distance.gt(-0.2) & distance.lt(1001.0)
            mask = ~is_short_term & ~distance_valid
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_169():
    error = ErrorDefinition(
        code='169',
        description='Local Authority (LA) of placement is not valid or is missing. Please check a valid postcode has been entered.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])

            # Because PL_LA is derived, it will always be valid if present
            mask = ~is_short_term & df['PL_LA'].isna()
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_179():
    error = ErrorDefinition(
        code='179',
        description='Placement location code is not a valid code.',
        affected_fields=['PL_LOCATION'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])

            # Because PL_LOCATION is derived, it will always be valid if present
            mask = ~is_short_term & df['PL_LOCATION'].isna()
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_1015():
    error = ErrorDefinition(
        code='1015',
        description='Placement provider is own provision but child not placed in own LA.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            local_authority = dfs['metadata']['localAuthority']

            placement_fostering_or_adoption = df['PLACE'].isin([
                'A3', 'A4', 'A5', 'A6', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6',
            ])
            own_provision = df['PLACE_PROVIDER'].eq('PR1')
            is_short_term = df['LS'].isin(['V3', 'V4'])
            is_pl_la = df['PL_LA'].eq(local_authority)

            checked_episodes = ~placement_fostering_or_adoption & ~is_short_term & own_provision
            checked_episodes = checked_episodes & df['LS'].notna() & df['PLACE'].notna()
            mask = checked_episodes & ~is_pl_la

            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_411():
    error = ErrorDefinition(
        code='411',
        description='Placement location code disagrees with LA of placement.',
        affected_fields=['PL_LOCATION'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            local_authority = dfs['metadata']['localAuthority']

            mask = df['PL_LOCATION'].eq('IN') & df['PL_LA'].ne(local_authority)

            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_420():
    error = ErrorDefinition(
        code='420',
        description='LA of placement completed but child is looked after under legal status V3 or V4.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            is_short_term = df['LS'].isin(['V3', 'V4'])

            mask = is_short_term & df['PL_LA'].notna()
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_355():
    error = ErrorDefinition(
        code='355',
        description='Episode appears to have lasted for less than 24 hours',
        affected_fields=['DECOM','DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = df['DECOM'].astype(str) == df['DEC'].astype(str)
            return {'Episodes': df.index[mask].tolist()}

    return error, _validate

def validate_586():
    error = ErrorDefinition(
        code='586',
        description='Dates of missing periods are before child’s date of birth.',
        affected_fields=['MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            df = dfs['Missing']   
            df['DOB'] = pd.to_datetime(df['DOB'],format='%d/%m/%Y',errors='coerce')
            df['MIS_START'] = pd.to_datetime(df['MIS_START'],format='%d/%m/%Y',errors='coerce')

            error_mask = df['MIS_START'].notna() & (df['MIS_START'] <= df['DOB'])
            return {'Missing': df.index[error_mask].to_list()}

    return error, _validate

def validate_630():
    error = ErrorDefinition(
        code='630',
        description='Information on previous permanence option should be returned.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'PrevPerm' not in dfs or 'Episodes' not in dfs:
            return {}
        else:        
            epi = dfs['Episodes']
            pre = dfs['PrevPerm']
            
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'],format='%d/%m/%Y',errors='coerce')

            epi = epi.reset_index()

            # Form the episode dataframe which has an 'RNE' of 'S' in this financial year
            epi_has_rne_of_S_in_year = epi[(epi['RNE'] == 'S') & (epi['DECOM'] >= collection_start)]
            # Merge to see 
            #1) which CHILD ids are missing from the PrevPerm file
            #2) which CHILD are in the prevPerm file, but don't have the LA_PERM/DATE_PERM field completed where they should be
            #3) which CHILD are in the PrevPerm file, but don't have the PREV_PERM field completed.
            merged_epi_preperm = epi_has_rne_of_S_in_year.merge(pre,on='CHILD',how='left',indicator=True)

            error_not_in_preperm = merged_epi_preperm['_merge'] == 'left_only'
            error_wrong_values_in_preperm = (merged_epi_preperm['PREV_PERM'] != 'Z1') & (merged_epi_preperm[['LA_PERM','DATE_PERM']].isna().any(axis=1))
            error_null_prev_perm = (merged_epi_preperm['_merge'] == 'both') & (merged_epi_preperm['PREV_PERM'].isna())

            error_mask = error_not_in_preperm | error_wrong_values_in_preperm | error_null_prev_perm

            error_list = merged_epi_preperm[error_mask]['index'].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {'Episodes': error_list}

    return error, _validate

def validate_501():
    error = ErrorDefinition(
        code='501',
        description='A new episode has started before the end date of the previous episode.',
        affected_fields=['DECOM','DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']   
            epi = epi.reset_index()
            epi['DECOM'] = pd.to_datetime(epi['DECOM'],format='%d/%m/%Y',errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'],format='%d/%m/%Y',errors='coerce')

            epi = epi.sort_values(['CHILD','DECOM'])

            epi_lead = epi.shift(1)
            epi_lead = epi_lead.reset_index()

            m_epi = epi.merge(epi_lead,left_on='index',right_on='level_0',suffixes=('', '_prev'))

            error_cohort = m_epi[(m_epi['CHILD'] == m_epi['CHILD_prev']) & (m_epi['DECOM'] < m_epi['DEC_prev'])]
            error_list = error_cohort['index'].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate

def validate_502():
    error = ErrorDefinition(
        code='502',
        description='Last year’s record ended with an open episode. The date on which that episode started does not match the start date of the first episode on this year’s record.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_last = dfs['Episodes_last']
            epi = epi.reset_index()

            epi['DECOM'] = pd.to_datetime(epi['DECOM'],format='%d/%m/%Y',errors='coerce')
            epi_last['DECOM'] = pd.to_datetime(epi_last['DECOM'],format='%d/%m/%Y',errors='coerce')

            epi_last_no_dec = epi_last[epi_last['DEC'].isna()]   

            epi_min_decoms_index = epi[['CHILD','DECOM']].groupby(['CHILD'])['DECOM'].idxmin()

            epi_min_decom_df = epi.loc[epi_min_decoms_index,:]

            merged_episodes = epi_min_decom_df.merge(epi_last_no_dec,on='CHILD',how='inner')
            error_cohort = merged_episodes[merged_episodes['DECOM_x'] != merged_episodes['DECOM_y']]

            error_list = error_cohort['index'].to_list()
            error_list = list(set(error_list))
            error_list.sort()
            
            return {'Episodes': error_list}

    return error, _validate

def validate_153():
    error = ErrorDefinition(
        code='153',
        description="All data items relating to a child's activity or accommodation after leaving care must be coded or left blank.",
        affected_fields=['IN_TOUCH','ACTIV','ACCOM'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}

        oc3 = dfs['OC3']

        oc3_not_na = (
            oc3['IN_TOUCH'].notna() &
            oc3['ACTIV'].notna() &
            oc3['ACCOM'].notna()
        )

        oc3_all_na = (
            oc3['IN_TOUCH'].isna() &
            oc3['ACTIV'].isna() &
            oc3['ACCOM'].isna()
        )


        validation_error = ~oc3_not_na & ~oc3_all_na

        validation_error_locations = oc3.index[validation_error]

        return {'OC3': validation_error_locations.to_list()}

    return error, _validate

def validate_166():
    error = ErrorDefinition(
        code = '166',
        description = "Date of review is invalid or blank.",
        affected_fields=['REVIEW'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}
        else:
            review = dfs['Reviews']

            error_mask = pd.to_datetime(review['REVIEW'], format='%d/%m/%Y', errors='coerce').isna()

            validation_error_locations = review.index[error_mask]

            return {'Reviews': validation_error_locations.to_list()}
    return error, _validate

def validate_174():
    error = ErrorDefinition(
        code = '174',
        description = "Mother's child date of birth is recorded but gender shows that the child is a male.",
        affected_fields=['SEX','MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            child_is_male = header['SEX'].astype(str) == '1'
            mc_dob_recorded = header['MC_DOB'].notna()

            error_mask = child_is_male & mc_dob_recorded

            validation_error_locations = header.index[error_mask]

            return {'Header': validation_error_locations.to_list()}
    return error, _validate

def validate_180():
    error = ErrorDefinition(
        code = '180',
        description = "Data entry for the strengths and difficulties questionnaire (SDQ) score is invalid.",
        affected_fields=['SDQ_SCORE'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            oc2['SDQ_SCORE'] = pd.to_numeric(oc2['SDQ_SCORE'], errors='coerce')

            error_mask = ~oc2['SDQ_SCORE'].isin(range(41))

            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}
    return error, _validate

def validate_181():
    error = ErrorDefinition(
        code = '181',
        description = "Data items relating to children looked after continuously for 12 months should be completed with a 0 or 1.",
        affected_fields=['CONVICTED','HEALTH_CHECK','IMMUNISATIONS','TEETH_CHECK','HEALTH_ASSESSMENT','SUBSTANCE_MISUSE','INTERVENTION_RECEIVED','INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            code_list = ['0', '1']

            mask = (
              (oc2['CONVICTED'].astype(str).isin(code_list) | oc2['CONVICTED'].isna()) &
              (oc2['HEALTH_CHECK'].astype(str).isin(code_list) | oc2['HEALTH_CHECK'].isna()) &
              (oc2['IMMUNISATIONS'].astype(str).isin(code_list) | oc2['IMMUNISATIONS'].isna()) &
              (oc2['TEETH_CHECK'].astype(str).isin(code_list) | oc2['TEETH_CHECK'].isna()) &
              (oc2['HEALTH_ASSESSMENT'].astype(str).isin(code_list) | oc2['HEALTH_ASSESSMENT'].isna()) &
              (oc2['SUBSTANCE_MISUSE'].astype(str).isin(code_list) | oc2['SUBSTANCE_MISUSE'].isna()) &
              (oc2['INTERVENTION_RECEIVED'].astype(str).isin(code_list) | oc2['INTERVENTION_RECEIVED'].isna()) &
              (oc2['INTERVENTION_OFFERED'].astype(str).isin(code_list) | oc2['INTERVENTION_OFFERED'].isna())
            )

            validation_error_mask = ~mask
            validation_error_locations = oc2.index[validation_error_mask]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate

def validate_192():
    error = ErrorDefinition(
        code = '192',
        description = "Child has been identified as having a substance misuse problem but the additional item on whether an intervention was received has been left blank.",
        affected_fields=['SUBSTANCE_MISUSE','INTERVENTION_RECEIVED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            misuse = oc2['SUBSTANCE_MISUSE'].astype(str) == '1'
            intervention_blank = oc2['INTERVENTION_RECEIVED'].isna()

            error_mask = misuse & intervention_blank
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}
    return error, _validate

def validate_193():
    error = ErrorDefinition(
        code = '193',
        description = "Child not identified as having a substance misuse problem but at least one of the two additional items on whether an intervention were offered and received have been completed.",
        affected_fields=['SUBSTANCE_MISUSE','INTERVENTION_RECEIVED','INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            no_substance_misuse = oc2['SUBSTANCE_MISUSE'].isna() | (oc2['SUBSTANCE_MISUSE'].astype(str) == '0')
            intervention_not_blank = oc2['INTERVENTION_RECEIVED'].notna() | oc2['INTERVENTION_OFFERED'].notna()

            error_mask = no_substance_misuse & intervention_not_blank
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate

def validate_197():
    error = ErrorDefinition(
        code = '197',
        description = "Reason for no Strengths and Difficulties (SDQ) score is not required if Strengths and Difficulties Questionnaire score is filled in.",
        affected_fields=['SDQ_SCORE','SDQ_REASON'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            sdq_filled_in = oc2['SDQ_SCORE'].notna()
            reason_filled_in = oc2['SDQ_REASON'].notna()

            error_mask = sdq_filled_in & reason_filled_in
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate

def validate_567():
    error = ErrorDefinition(
        code='567',
        description='The date that the missing episode or episode that the child was away from placement without authorisation ended is before the date that it started.',
        affected_fields=['MIS_START','MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'],format='%d/%m/%Y',errors='coerce')
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'],format='%d/%m/%Y',errors='coerce')

            mis_error = mis[mis['MIS_START'] > mis['MIS_END']]

            return {'Missing': mis_error.index.to_list()}

    return error, _validate

def validate_304():
    error = ErrorDefinition(
        code='304',
        description='Date unaccompanied asylum-seeking child (UASC) status ceased must be on or before the 18th birthday of a child.',
        affected_fields=['DUC'],
    )

    def _validate(dfs):
        if 'UASC' not in dfs:
            return {}
        else:
            uasc = dfs['UASC']
            uasc['DOB'] = pd.to_datetime(uasc['DOB'],format='%d/%m/%Y',errors='coerce')
            uasc['DUC'] = pd.to_datetime(uasc['DUC'],format='%d/%m/%Y',errors='coerce')

            mask = uasc['DUC'].notna() & (uasc['DUC'] > uasc['DOB'] + pd.offsets.DateOffset(years=18))

            return {'UASC': uasc.index[mask].to_list()}

    return error, _validate

def validate_333():
    error = ErrorDefinition(
        code='333',
        description='Date should be placed for adoption must be on or prior to the date of matching child with adopter(s).',
        affected_fields=['DATE_INT'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            adt = dfs['AD1']
            adt['DATE_MATCH'] = pd.to_datetime(adt['DATE_MATCH'],format='%d/%m/%Y',errors='coerce')
            adt['DATE_INT'] = pd.to_datetime(adt['DATE_INT'],format='%d/%m/%Y',errors='coerce')

            #If <DATE_MATCH> provided, then <DATE_INT> must also be provided and be <= <DATE_MATCH>
            mask1 = adt['DATE_MATCH'].notna() & adt['DATE_INT'].isna()
            mask2 = adt['DATE_MATCH'].notna() & adt['DATE_INT'].notna() & (adt['DATE_INT'] > adt['DATE_MATCH'])
            mask = mask1 | mask2

            return {'AD1': adt.index[mask].to_list()}

    return error, _validate

def validate_1011():
    error = ErrorDefinition(
        code='1011',
        description='This child is recorded as having his/her care transferred to another local authority for the final episode and therefore should not have the care leaver information completed.',
        affected_fields=['IN_TOUCH','ACTIV','ACCOM'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            oc3 = dfs['OC3']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            #If final <REC> = 'E3' then <IN_TOUCH>; <ACTIV> and <ACCOM> should not be provided
            epi.sort_values(['CHILD','DECOM'],inplace=True)
            grouped_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_decom_only = epi.loc[epi.index.isin(grouped_decom_by_child), :]
            E3_is_last = max_decom_only[max_decom_only['REC'] == 'E3']

            oc3.reset_index(inplace=True)
            cohort_to_check = oc3.merge(E3_is_last,on='CHILD',how='inner')
            error_mask = cohort_to_check[['IN_TOUCH','ACTIV','ACCOM']].notna().any(axis=1)

            error_list = cohort_to_check['index'][error_mask].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {'OC3': error_list}

    return error, _validate

def validate_574():
    error = ErrorDefinition(
        code='574',
        description='A new missing/away from placement without authorisation period cannot start when the previous missing/away from placement without authorisation period is still open. Missing/away from placement without authorisation periods should also not overlap.',
        affected_fields=['MIS_START','MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:

            mis = dfs['Missing']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'], format='%d/%m/%Y', errors='coerce')

            mis.sort_values(['CHILD','MIS_START'],inplace=True)

            mis.reset_index(inplace=True)
            mis.reset_index(inplace=True)  #Twice on purpose

            mis['LAG_INDEX'] = mis['level_0'].shift(-1)

            lag_mis = mis.merge(mis,how='inner',left_on='level_0',right_on='LAG_INDEX',suffixes=['','_PREV'])

            #We're only interested in cases where there is more than one row for a child.
            lag_mis = lag_mis[lag_mis['CHILD'] == lag_mis['CHILD_PREV']]

            #A previous MIS_END date is null
            mask1 = lag_mis['MIS_END_PREV'].isna()
            #MIS_START is before previous MIS_END (overlapping dates)
            mask2 = lag_mis['MIS_START'] < lag_mis['MIS_END_PREV']

            mask = mask1 | mask2

            error_list = lag_mis['index'][mask].to_list()
            error_list.sort()
            return {'Missing': error_list}

    return error, _validate

def validate_564():
    error = ErrorDefinition(
        code='564',
        description='Child was missing or away from placement without authorisation and the date started is blank.',
        affected_fields=['MISSING','MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            error_mask = mis['MISSING'].isin(['M','A','m','a']) & mis['MIS_START'].isna()
            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate

def validate_566():
    error = ErrorDefinition(
        code='566',
        description='The date that the child'+chr(39)+'s episode of being missing or away from placement without authorisation ended has been completed but whether the child was missing or away without authorisation has not been completed.',
        affected_fields=['MISSING','MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            error_mask = mis['MISSING'].isna() & mis['MIS_END'].notna()
            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate

def validate_436():
    error = ErrorDefinition(
        code='436',
        description='Reason for new episode is that both child’s placement and legal status have changed, but this is not reflected in the episode data.',
        affected_fields=['RNE','LS','PLACE','PL_POST','URN','PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:

            epi = dfs['Episodes']
            epi['DECOM'] =  pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD','DECOM'],inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)
            epi.fillna(value={"LS": '*', "PLACE": '*', "PL_POST": '*', "URN": '*', "PLACE_PROVIDER": '*'},inplace=True)
            epi_merge = epi.merge(epi,how='inner',left_on='level_0',right_on='LAG_INDEX',suffixes=['','_PRE'])

            epi_multi_row = epi_merge[epi_merge['CHILD'] == epi_merge['CHILD_PRE']]
            epi_has_B_U = epi_multi_row[epi_multi_row['RNE'].isin(['U','B'])]

            mask_ls = epi_has_B_U['LS'] == epi_has_B_U['LS_PRE']

            mask1 = epi_has_B_U['PLACE'] == epi_has_B_U['PLACE_PRE']
            mask2 = epi_has_B_U['PL_POST'] == epi_has_B_U['PL_POST_PRE']
            mask3 = epi_has_B_U['URN'] == epi_has_B_U['URN_PRE']
            mask4 = epi_has_B_U['PLACE_PROVIDER'] == epi_has_B_U['PLACE_PROVIDER_PRE']

            error_mask = mask_ls | ( mask1 & mask2 & mask3 & mask4 )

            error_list = epi_has_B_U[error_mask]['index'].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate

def validate_570():
    error = ErrorDefinition(
        code = '570',
        description = 'The date that the child started to be missing or away from placement without authorisation is after the end of the collection year.',
        affected_fields=['MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'],format='%d/%m/%Y',errors='coerce')

            mis['MIS_START'] =  pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            error_mask = mis['MIS_START'] > collection_end

            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate

def validate_531():
    error = ErrorDefinition(
        code='531',
        description='A placement provider code of PR5 cannot be associated with placements P1.',
        affected_fields=['PLACE','PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE']=='P1') & (epi['PLACE_PROVIDER'] =='PR5')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate

def validate_542():
    error = ErrorDefinition(
        code='542',
        description='A child aged under 10 at 31 March should not have conviction information completed.',
        affected_fields=['CONVICTED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'],format='%d/%m/%Y',errors='coerce')
            error_mask = ( oc2['DOB'] + pd.offsets.DateOffset(years=10) > collection_end ) & oc2['CONVICTED'].notna()
            return {'OC2': oc2.index[error_mask].to_list()}

    return error, _validate

def validate_620():
    error = ErrorDefinition(
        code='620',
        description='Child has been recorded as a mother, but date of birth shows that the mother is under 11 years of age.',
        affected_fields=['DOB','MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            hea = dfs['Header']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'],format='%d/%m/%Y',errors='coerce')
            hea['DOB'] =  pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')

            hea_mother = hea[hea['MOTHER'].astype(str) == '1']
            error_cohort = (hea_mother['DOB'] + pd.offsets.DateOffset(years=11)) > collection_start

            return {'Header': hea_mother.index[error_cohort].to_list()}

    return error, _validate

def validate_225():
    error = ErrorDefinition(
        code='225',
        description='Reason for placement change must be recorded.',
        affected_fields=['REASON_PLACE_CHANGE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD','DECOM'],inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(1)
            m_epi = epi.merge(epi,how='inner',left_on='level_0',right_on='LAG_INDEX',suffixes=['','_NEXT'])
            m_epi = m_epi[m_epi['CHILD'] == m_epi['CHILD_NEXT']]

            mask_is_X1 = m_epi['REC'] == 'X1'
            mask_null_place_chg = m_epi['REASON_PLACE_CHANGE'].isna()
            mask_place_not_T = ~m_epi['PLACE'].isin(['T0','T1','T2','T3','T4'])
            mask_next_is_PBTU = m_epi['RNE_NEXT'].isin(['P','B','T','U'])
            mask_next_place_not_T = ~m_epi['PLACE_NEXT'].isin(['T0','T1','T2','T3','T4'])

            error_mask = mask_is_X1 & mask_null_place_chg & mask_place_not_T & mask_next_is_PBTU & mask_next_place_not_T

            error_list = m_epi['index'][error_mask].to_list()
            return {'Episodes': error_list}

    return error, _validate

def validate_353():
    error = ErrorDefinition(
        code='353',
        description='No episode submitted can start before 14 October 1991.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            min_decom_allowed = pd.to_datetime('14/10/1991', format='%d/%m/%Y', errors='coerce')
            error_mask = epi['DECOM'] < min_decom_allowed
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate

def validate_528():
    error = ErrorDefinition(
        code='528',
        description='A placement provider code of PR2 cannot be associated with placements P1, R2 or R5.',
        affected_fields=['PLACE','PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['P1','R2','R5'])) & (epi['PLACE_PROVIDER'] =='PR2')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate

def validate_527():
    error = ErrorDefinition(
        code='527',
        description='A placement provider code of PR1 cannot be associated with placements P1, R2 or R5.',
        affected_fields=['PLACE','PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['P1','R2','R5'])) & (epi['PLACE_PROVIDER'] =='PR1')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate

def validate_359():
    error = ErrorDefinition(
        code='359',
        description='Child being looked after following 18th birthday must be accommodated under section 20(5) of the Children Act 1989 in a community home.',
        affected_fields=['DEC','LS','PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            hea = dfs['Header']
            hea['DOB'] =  pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'],format='%d/%m/%Y',errors='coerce')

            epi.reset_index(inplace=True)
            epi = epi.merge(hea,on='CHILD',how='left',suffixes=['','_HEA'])

            mask_older_18 = (epi['DOB'] + pd.offsets.DateOffset(years=18)) < collection_end
            mask_null_dec = epi['DEC'].isna()
            mask_is_V2_K2 = (epi['LS'] == 'V2') & (epi['PLACE'] == 'K2')

            error_mask = mask_older_18 & mask_null_dec & ~mask_is_V2_K2
            error_list = epi['index'][error_mask].to_list()
            error_list = list(set(error_list))

            return {'Episodes': error_list}

    return error, _validate

def validate_562():
    error = ErrorDefinition(
        code='562',
        description='Episode commenced before the start of the current collection year but there is a missing continuous episode in the previous year.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_last = dfs['Episodes_last']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi_last['DECOM'] = pd.to_datetime(epi_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'],format='%d/%m/%Y',errors='coerce')

            epi.reset_index(inplace=True)
            epi = epi[epi['DECOM'] < collection_start]

            grp_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmin(skipna=True)
            min_decom = epi.loc[epi.index.isin(grp_decom_by_child), :]

            grp_last_decom_by_child = epi_last.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_last_decom = epi_last.loc[epi_last.index.isin(grp_last_decom_by_child), :]

            merged_co = min_decom.merge(max_last_decom,how='left', on=['CHILD', 'DECOM'], suffixes=['', '_PRE'], indicator=True)
            error_cohort = merged_co[merged_co['_merge'] == 'left_only']

            error_list = error_cohort['index'].to_list()
            error_list = list(set(error_list))
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate

def validate_408():
    error = ErrorDefinition(
        code='408',
        description='Child is placed for adoption with a placement order, but no placement order has been recorded.',
        affected_fields=['PLACE','LS'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = epi['PLACE'].isin(['A5','A6']) & (epi['LS'] !='E1')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate

def validate_380():
    error = ErrorDefinition(
        code='380',
        description='A period of care cannot start with a temporary placement.',
        affected_fields=['PLACE','RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['T0','T1','T2','T3','T4'])) & (~epi['RNE'].isin(['P','B']))
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate

def validate_381():
    error = ErrorDefinition(
        code='381',
        description='A period of care cannot end with a temporary placement.',
        affected_fields=['PLACE','REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['T0','T1','T2','T3','T4'])) & (epi['REC'] != 'X1') & (epi['REC'].notna())
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_504():
    error = ErrorDefinition(
        code='504',
        description='The category of need code differs from that reported at start of current period of being looked after',
        affected_fields=['CIN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD','DECOM'],inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(1)

            merge_epi = epi.merge(epi,how='inner',left_on='LAG_INDEX',right_on='level_0',suffixes=['','_PRE'])
            merge_epi = merge_epi[merge_epi['CHILD'] == merge_epi['CHILD_PRE']]
            merge_epi = merge_epi[(merge_epi['REC_PRE'] == 'X1') & (merge_epi['DEC_PRE'] == merge_epi['DECOM'])]
            error_cohort = merge_epi[merge_epi['CIN'] != merge_epi['CIN_PRE']]
            error_list = error_cohort['index'].unique().tolist()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate

def validate_431():
    error = ErrorDefinition(
        code='431',
        description='The reason for new episode is started to be looked after, but the previous episode ended on the same day.',
        affected_fields=['RNE','DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD','DECOM'],inplace=True)

            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)

            m_epi = epi.merge(epi,how='inner',left_on='level_0',right_on='LAG_INDEX',suffixes=['','_PREV'])

            m_epi = m_epi[(m_epi['CHILD'] == m_epi['CHILD_PREV']) & (m_epi['RNE'] == 'S')]
            error_mask = m_epi['DECOM'] <= m_epi['DEC_PREV']
            error_list = m_epi['index'][error_mask].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate

def validate_503_Generic(subval):
    Gen_503_dict = {
        "A": {
            "Desc": "The reason for new episode in the first episode does not match open episode at end of last year.",
            "Fields": 'RNE'},
        "B": {"Desc": "The legal status in the first episode does not match open episode at end of last year.",
              "Fields": 'LS'},
        "C": {"Desc": "The category of need in the first episode does not match open episode at end of last year.",
              "Fields": 'CIN'},
        "D": {"Desc": "The placement type in the first episode does not match open episode at end of last year",
              "Fields": 'PLACE'},
        "E": {"Desc": "The placement provider in the first episode does not match open episode at end of last year.",
              "Fields": 'PLACE_PROVIDER'},
        "F": {"Desc": "The Ofsted URN in the  first episode does not match open episode at end of last year.",
              "Fields": 'URN'},
    }
    error = ErrorDefinition(
        code='503'+subval,
        description=Gen_503_dict[subval]['Desc'],
        affected_fields=[Gen_503_dict[subval]['Fields']],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_last = dfs['Episodes_last']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi_last['DECOM'] = pd.to_datetime(epi_last['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)

            grp_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmin(skipna=True)
            min_decom = epi.loc[epi.index.isin(grp_decom_by_child), :]

            grp_last_decom_by_child = epi_last.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_last_decom = epi_last.loc[epi_last.index.isin(grp_last_decom_by_child), :]

            merged_co = min_decom.merge(max_last_decom, how='inner', on=['CHILD', 'DECOM'], suffixes=['', '_PRE'])

            this_one = Gen_503_dict[subval]['Fields']
            pre_one = this_one + '_PRE'

            err_mask = merged_co[this_one] != merged_co[pre_one]
            err_list = merged_co['index'][err_mask].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate

def validate_503A():
    return validate_503_Generic('A')

def validate_503B():
    return validate_503_Generic('B')

def validate_503C():
    return validate_503_Generic('C')

def validate_503D():
    return validate_503_Generic('D')

def validate_503E():
    return validate_503_Generic('E')

def validate_503F():
    return validate_503_Generic('F')

def validate_526():
    error = ErrorDefinition(
        code='526',
        description='Child is missing a placement provider code for at least one episode.',
        affected_fields=['PLACE','PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = ~epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4', 'Z1']) & epi['PLACE_PROVIDER'].isna()
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_370to376and379(subval):
    Gen_370_dict = {
    "370": {"Desc": "Child in independent living should be at least 15.",
        "P_Code": 'P2', "Y_gap": 15},
    "371": {"Desc": "Child in semi-independent living accommodation not subject to children’s homes regulations " +
        "should be at least 14.",
        "P_Code": 'H5', "Y_gap": 14},
    "372": {"Desc": "Child in youth custody or prison should be at least 10.",
        "P_Code": 'R5', "Y_gap": 10},
    "373": {"Desc": "Child placed in a school should be at least 4 years old.",
        "P_Code": 'S1', "Y_gap": 4},
    "374": {"Desc": "Child in residential employment should be at least 14 years old.",
        "P_Code": 'P3', "Y_gap": 14},
    "375": {"Desc": "Hospitalisation coded as a temporary placement exceeds six weeks.",
        "P_Code": 'T1', "Y_gap": 42},
    "376": {"Desc": "Temporary placements coded as being due to holiday of usual foster carer(s) cannot exceed " +
        "three weeks.",
        "P_Code": 'T3', "Y_gap": 21},
    "379": {"Desc": "Temporary placements for unspecified reason (placement code T4) cannot exceed seven days.",
        "P_Code": 'T4', "Y_gap": 7},
    }
    error = ErrorDefinition(
        code=str(subval),
        description=Gen_370_dict[subval]['Desc'],
        affected_fields=['DECOM', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            hea = dfs['Header']
            hea['DOB'] = pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            epi.reset_index(inplace=True)
            epi_p2 = epi[epi['PLACE'] == Gen_370_dict[subval]['P_Code']]
            merged_e = epi_p2.merge(hea, how='inner', on='CHILD')
            merged_e = merged_e.dropna(subset=['DECOM', 'DEC', 'DOB'])
            if subval in  ['370', '371', '372', '373', '374']:
                error_mask = merged_e['DECOM'] < (merged_e['DOB'] +
                    pd.offsets.DateOffset(years=Gen_370_dict[subval]['Y_gap']))
            else:
                error_mask = merged_e['DEC'] > (merged_e['DECOM'] +
                    pd.offsets.DateOffset(days=Gen_370_dict[subval]['Y_gap']))
            return {'Episodes': merged_e['index'][error_mask].unique().tolist()}

    return error, _validate

def validate_370():
    return validate_370to376and379('370')

def validate_371():
    return validate_370to376and379('371')

def validate_372():
    return validate_370to376and379('372')

def validate_373():
    return validate_370to376and379('373')

def validate_374():
    return validate_370to376and379('374')

def validate_375():
    return validate_370to376and379('375')

def validate_376():
    return validate_370to376and379('376')

def validate_379():
    return validate_370to376and379('379')
