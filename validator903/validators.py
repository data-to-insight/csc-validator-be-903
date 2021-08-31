import pandas as pd
from .types import ErrorDefinition

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
        code_list = [1, 2]

        mask = header['SEX'].isin(code_list)

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


def validate_214():
    error = ErrorDefinition(
        code='214',
        description='Placement location information not required.',
        affected_fields=['PL_POST','URN'],
    )

    def _validate(dfs):
        if 'Episode' not in dfs:
            return {}
        else:
            df = dfs['Episode']
            mask = df['LS'].isin(['V3','V4']) & ((df['PL_POST'].notna()) | (df['URN'].notna()))
            return {'Episode': df.index[mask].tolist()}

    return error, _validate

def validate_222():
    error = ErrorDefinition(
        code='222',
        description='Ofsted Unique reference number (URN) should not be recorded for this placement type.',
        affected_fields=['URN'],
    )

    def _validate(dfs):
        if 'Episode' not in dfs:
            return {}
        else:
            df = dfs['Episode']
            place_code_list = ['H5','P1','P2','P3','R1','R2','R5','T0','T1','T2','T3','T4','Z1']
            mask = (df['PLACE'].isin(place_code_list)) & (df['URN'].notna()) & (df['URN'] != 'XXXXXX')
            return {'Episode': df.index[mask].tolist()}

    return error, _validate

def validate_366():
    error = ErrorDefinition(
        code='366',
        description='A child cannot change placement during the course of an individual short-term respite break.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'Episode' not in dfs:
            return {}
        else:
            df = dfs['Episode']
            mask = (df['LS'] == 'V3') & (df['RNE'] != 'S')
            return {'Episode': df.index[mask].tolist()}

    return error, _validate