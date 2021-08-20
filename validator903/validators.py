import pandas as pd
from .types import ErrorDefinition

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
        code_list = ['S', 'P', 'L', 'T', 'B']

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

def validate_392c():
    error = ErrorDefinition(
        code='392c',
        description='Postcode(s) provided are invalid.',
        affected_fields=['HOME_POST', 'PL_POST'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'postcodes' not in dfs['metadata']:
            return {}
        else:
            episodes = dfs['Episodes']
            postcode_list = set(dfs['metadata']['postcodes']['pcd'])

            home_valid = episodes['HOME_POST'].apply(lambda x: x in postcode_list)
            pl_valid = episodes['PL_POST'].apply(lambda x: x in postcode_list)

            error_mask = ~home_valid | ~pl_valid

            return {'Episodes': episodes.index[error_mask].tolist()}

    return error, _validate

def validate_388():
    error = ErrorDefinition(
        code='388',
        description='Reason episode ceased is coded new episode begins, but there is no continuation episode.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Episode' not in dfs:
            return {}
        else:
            df = dfs['Episode']
            error_rows = (df['CHILD'] != df['CHILD']) 
            for x in df['CHILD'].unique():
              #Form a loop through each unique child id
              this_child = df[df['CHILD'] == x].sort_values('DECOM')
              #Focus on each child in turn (thischild)
              if len(this_child['CHILD']) >= 2:
              #Check this child has at least 2 rows (otherwise it's fine)
                for inchild in range(len(this_child['CHILD']) - 1):  
                  if (this_child['DEC'].iloc[inchild] == this_child['DECOM'].iloc[inchild + 1]) and this_child['REC'].iloc[inchild] != 'X1':
                    error_here = (df['CHILD'] == this_child['CHILD'].iloc[inchild]) & (df['DEC'] == this_child['DEC'].iloc[inchild])
                    error_rows = error_rows | error_here
            return {'Episode': df.index[error_rows].tolist()}
    
    return error, _validate


def validate_213 ():
    error = ErrorDefinition(
        code='213',
        description='Placement provider information not required.',
        affected_fields=['PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episode' not in dfs:
          return {}
        else:
          df = dfs['Episode']
          mask = df['PLACE'].isin(['T0','T1','T2','T3','T4','Z1']) & df['PLACE_PROVIDER'].notna()
          return {'Episode': df.index[mask].tolist()}
    
    return error, _validate

def validate_214 ():
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
          mask = df['LS'].isin(['V3','V4']) & (df['PL_POST'].notna() | df['URN'].notna())
          return {'Episode': df.index[mask].tolist()}

    return error, _validate

def validate_222 ():
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
          mask = (df['PLACE'].isin(['H5','P1','P2','P3','R1','R2','R5','T0','T1','T2','T3','T4','Z1'])) & (df['URN'].notna()) & (df['URN'] != 'XXXXXX')
          return {'Episode': df.index[mask].tolist()}

    return error, _validate



def validate_366 ():
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
