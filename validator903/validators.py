import pandas as pd

from .datastore import merge_postcodes
from .types import ErrorDefinition, IntegrityCheckDefinition, MissingMetadataError
from .utils import add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column  # Check 'Episodes' present before use!


# EPI is an undocumented rule in the DFE portal. It checks whether each Child ID in the Header file exists in either the Episodes or OC3 file.
def validate_EPI():
    error = ErrorDefinition(
        code='EPI',
        description='WARNING: Episodes need to be loaded for this child before further validation is possible '
                    '[NOTE: This refers to the DfE portal - here, all checks that can be performed with only the '
                    'available data will be.]',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            if 'Episodes' not in dfs:
                episodes = pd.DataFrame(columns=['CHILD'])
            else:
                episodes = dfs['Episodes']

            if 'OC3' not in dfs:
                oc3 = pd.DataFrame(columns=['CHILD'])
            else:
                oc3 = dfs['OC3']

            header['index_header'] = header.index

            merged = header.merge(episodes['CHILD'], on='CHILD', indicator='_merge_eps', how='left',
                                  suffixes=['', '_episodes'])

            merged = merged.merge(oc3['CHILD'], on='CHILD', indicator='_merge_oc3', how='left', suffixes=['', '_oc3'])

            mask = (merged['_merge_eps'] == 'left_only') & (merged['_merge_oc3'] == 'left_only')
            eps_error_locations = merged.loc[mask, 'index_header']
            return {'Header': eps_error_locations.unique().tolist()}
    return error, _validate


#INT are non-DFE rules created for internal validation in the tool only.
def validate_INT01():
    error = IntegrityCheckDefinition(
        code='INT01',
        description='Data Integrity Check: Child in AD1 does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['AD1']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'AD1': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT02():
    error = IntegrityCheckDefinition(
        code='INT02',
        description='Internal Check: Child in PlacedAdoption does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['PlacedAdoption']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'PlacedAdoption': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT03():
    error = IntegrityCheckDefinition(
        code='INT03',
        description='Internal Check: Child in Episodes does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['Episodes']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'Episodes': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT04():
    error = IntegrityCheckDefinition(
        code='INT04',
        description='Internal Check: Child in Missing does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['Missing']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'Missing': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT05():
    error = IntegrityCheckDefinition(
        code='INT05',
        description='Internal Check: Child in OC2 does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'OC2' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['OC2']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'OC2': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT06():
    error = IntegrityCheckDefinition(
        code='INT06',
        description='Internal Check: Child in OC3 does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['OC3']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'OC3': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT07():
    error = IntegrityCheckDefinition(
        code='INT07',
        description='Internal Check: Child in PrevPerm does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'PrevPerm' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['PrevPerm']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'PrevPerm': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT08():
    error = IntegrityCheckDefinition(
        code='INT08',
        description='Internal Check: Child in Reviews does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Reviews' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['Reviews']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'Reviews': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT09():
    error = IntegrityCheckDefinition(
        code='INT09',
        description='Internal Check: Child in UASC does not exist in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'UASC' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['UASC']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = merged['_merge'] == 'right_only'
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'UASC': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT11():
    error = IntegrityCheckDefinition(
        code='INT11',
        description='Internal Check: DOB in AD1 is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['AD1']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'AD1': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT12():
    error = IntegrityCheckDefinition(
        code='INT12',
        description='Internal Check: DOB in PlacedAdoption is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['PlacedAdoption']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'PlacedAdoption': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT13():
    error = IntegrityCheckDefinition(
        code='INT13',
        description='Internal Check: DOB in Missing is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['Missing']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'Missing': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT14():
    error = IntegrityCheckDefinition(
        code='INT14',
        description='Internal Check: DOB in OC2 is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'OC2' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['OC2']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'OC2': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT15():
    error = IntegrityCheckDefinition(
        code='INT15',
        description='Internal Check: DOB in OC3 is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['OC3']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'OC3': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT16():
    error = IntegrityCheckDefinition(
        code='INT16',
        description='Internal Check: DOB in PrevPerm is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'PrevPerm' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['PrevPerm']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'PrevPerm': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT17():
    error = IntegrityCheckDefinition(
        code='INT17',
        description='Internal Check: DOB in Reviews is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Reviews' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['Reviews']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'Reviews': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT18():
    error = IntegrityCheckDefinition(
        code='INT18',
        description='Internal Check: DOB in UASC is different to DOB in Header.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'UASC' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['UASC']

            header['DOB'] =  pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            file['DOB'] =  pd.to_datetime(file['DOB'], format='%d/%m/%Y', errors='coerce')

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'DOB', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['DOB_header'] != merged['DOB_file']) & (merged['DOB_header'].notna() & merged['DOB_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'UASC': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT21():
    error = IntegrityCheckDefinition(
        code='INT21',
        description='Internal Check: SEX in UASC is different to SEX in Header.',
        affected_fields=['SEX'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'UASC' not in dfs:
            return {}
        else:
            header = dfs['Header']
            file = dfs['UASC']

            file['index_file'] = file.index

            merged = header.merge(file[['CHILD', 'SEX', 'index_file']], on='CHILD', indicator=True, how='right', suffixes=['_header', '_file'])

            mask = (merged['SEX_header'] != merged['SEX_file']) & (merged['SEX_header'].notna() & merged['SEX_file'].notna()) & (merged['_merge'] != 'right_only')
            eps_error_locations = merged.loc[mask, 'index_file']
            return {'UASC': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT31():
    error = IntegrityCheckDefinition(
        code='INT31',
        description='Internal Check: Child should only exist once in AD1.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            file = dfs['AD1']

            file['index_file'] = file.index

            file['CHILD_COUNT'] = file.groupby('CHILD')['CHILD'].transform('count')

            mask = (file['CHILD_COUNT'] > 1)
            eps_error_locations = file.loc[mask, 'index_file']
            return {'AD1': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT32():
    error = IntegrityCheckDefinition(
        code='INT32',
        description='Internal Check: Child should only exist once in Header.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            file = dfs['Header']

            file['index_file'] = file.index

            file['CHILD_COUNT'] = file.groupby('CHILD')['CHILD'].transform('count')

            mask = (file['CHILD_COUNT'] > 1)
            eps_error_locations = file.loc[mask, 'index_file']
            return {'Header': eps_error_locations.unique().tolist()}

    return error, _validate

def validate_INT33():
    error = IntegrityCheckDefinition(
        code='INT33',
        description='Internal Check: Child should only exist once in OC2.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            file = dfs['OC2']

            file['index_file'] = file.index

            file['CHILD_COUNT'] = file.groupby('CHILD')['CHILD'].transform('count')

            mask = (file['CHILD_COUNT'] > 1)
            eps_error_locations = file.loc[mask, 'index_file']
            return {'OC2': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT34():
    error = IntegrityCheckDefinition(
        code='INT34',
        description='Internal Check: Child should only exist once in OC3.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        else:
            file = dfs['OC3']

            file['index_file'] = file.index

            file['CHILD_COUNT'] = file.groupby('CHILD')['CHILD'].transform('count')

            mask = (file['CHILD_COUNT'] > 1)
            eps_error_locations = file.loc[mask, 'index_file']
            return {'OC3': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT35():
    error = IntegrityCheckDefinition(
        code='INT35',
        description='Internal Check: Child should only exist once in PrevPerm.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'PrevPerm' not in dfs:
            return {}
        else:
            file = dfs['PrevPerm']

            file['index_file'] = file.index

            file['CHILD_COUNT'] = file.groupby('CHILD')['CHILD'].transform('count')

            mask = (file['CHILD_COUNT'] > 1)
            eps_error_locations = file.loc[mask, 'index_file']
            return {'PrevPerm': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_INT36():
    error = IntegrityCheckDefinition(
        code='INT36',
        description='Internal Check: Child should only exist once in UASC.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'UASC' not in dfs:
            return {}
        else:
            file = dfs['UASC']

            file['index_file'] = file.index

            file['CHILD_COUNT'] = file.groupby('CHILD')['CHILD'].transform('count')

            mask = (file['CHILD_COUNT'] > 1)
            eps_error_locations = file.loc[mask, 'index_file']
            return {'UASC': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_633():
    error = ErrorDefinition(
      code = '633',
      description = 'Local authority code where previous permanence option was arranged is not a valid value.',
      affected_fields = ['LA_PERM']
    )
    def _validate(dfs):
        if 'PrevPerm' not in dfs:
            return {}
        else:
            prevperm = dfs['PrevPerm']
            la_codes = '800,889,822,301,304,303,330,825,837,302,846,370,350,890,867,380,305,801,351,873,823,895,896,' \
                       '381,909,202,908,331,306,841,830,831,878,371,835,332,840,307,308,811,881,845,390,916,203,876,' \
                       '850,311,204,884,312,205,313,805,919,310,309,420,921,206,207,886,810,382,314,340,888,208,856,' \
                       '383,855,209,925,341,201,821,352,806,887,826,315,929,812,391,926,892,813,802,928,891,392,316,' \
                       '815,353,931,879,836,851,874,807,354,317,870,318,372,857,333,935,343,803,373,342,893,356,355,' \
                       '871,394,334,933,882,936,861,852,319,860,808,393,866,210,357,894,883,880,358,211,937,869,320,' \
                       '359,865,384,335,336,212,868,872,885,344,877,213,938,816,999'
            out_of_uk_codes = ['WAL', 'SCO', 'NUK', 'NIR']
            valid_values = la_codes.split(',') + out_of_uk_codes

            # Where provided <LA_PERM> must be a valid value
            mask = prevperm['LA_PERM'].notna() & (~prevperm['LA_PERM'].astype('str').isin(valid_values))

            # error locations
            error_locs = prevperm.index[mask]
            return {'PrevPerm': error_locs.tolist()}
    return error, _validate


def validate_426():
    error = ErrorDefinition(
        code='426',
        description='A child receiving respite care cannot be recorded under a legal status of V3 and V4 in ' +
                    'the same year.',
        affected_fields=['LS'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_v3 = epi[epi['LS'] == 'V3']
            epi_v4 = epi[epi['LS'] == 'V4']

            m_coh = epi_v3.merge(epi_v4, on='CHILD', how='inner')
            err_child = m_coh['CHILD'].unique().tolist()

            err_l1 = epi_v3[epi_v3['CHILD'].isin(err_child)].index.tolist()
            err_l2 = epi_v4[epi_v4['CHILD'].isin(err_child)].index.tolist()

            err_list = err_l1 + err_l2
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


#!# big potential false positives, as this only operates on the current and previous year data
def validate_1002():
    error = ErrorDefinition(
        code='1002',
        description='This child has no previous episodes of care, therefore should not have care leaver information recorded. '
                     '[NOTE: This tool can only test the current and previous year data loaded into the tool - this '
                    'check may generate false positives if a child had episodes prior to last year\'s collection.]',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC3' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            oc3 = dfs['OC3']

            episodes_last = dfs['Episodes_last']
            has_previous_episodes = oc3['CHILD'].isin(episodes_last['CHILD'])
            has_current_episodes = oc3['CHILD'].isin(episodes['CHILD'])
            error_mask = ~has_current_episodes & ~has_previous_episodes

            validation_error_locations = oc3.index[error_mask]

            return {'OC3': validation_error_locations.tolist()}

    return error, _validate


# !# False positives could be generated by 164 if child was UASC in last 2 years but data not provided
def validate_164():
    error = ErrorDefinition(
        code='164',
        description='Distance is not valid. Please check a valid postcode has been entered. [NOTE: This check will result in false positives for children formerly UASC not identified as such in loaded data]',
        affected_fields=['PL_DISTANCE'],
    )

    # If not (<UASC> = '1' or <COLLECTION_YEAR> -1 <UASC> = '1' or <COLLECTION_YEAR> -2 <UASC> = '1') and if <LS> not = 'V3' or 'V4' then <PL_DISTANCE> must be between '0.0' and '999.9' Note: <PL_DISTANCE> is a calculated value based on Postcode.
    def _validate(dfs):
        # Header_last also used if present
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            # Note the initial positions. Freeze a copy of the index values into a column
            epi['orig_idx'] = epi.index

            # Work out who is UASC or formerly UASC
            header = pd.DataFrame()
            if 'Header' in dfs:
                header_current = dfs['Header']
                header = pd.concat((header, header_current), axis=0)
            elif 'UASC' in dfs:
                uasc = dfs['UASC']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'Header_last' in dfs:
                header = pd.concat((header, dfs['Header_last']), axis=0)
            elif 'UASC_last' in dfs:
                uasc = dfs['UASC_last']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'UASC' in header.columns:
                header = header[header.UASC == '1'].drop_duplicates('CHILD')
                # drop all CHILD IDs that ever have UASC == 1
                epi = (epi
                       .merge(header[['CHILD']], how='left', on='CHILD', indicator=True)
                       .query('_merge == "left_only"'))
            else:
                # if theres no UASC column in header, either from XML data, inferred for CSV in ingress, or added above
                # then we can't identify anyone as UASC/formerly UASC
                return {}
            # PL_DISTANCE is added when the uploaded files are read into the tool. The code that does this is found in datastore.py
            epi = epi[epi['PL_DISTANCE'].notna()]
            check_in_range = (epi['PL_DISTANCE'].astype('float') < 0.0) | (epi['PL_DISTANCE'].astype('float') > 999.9)
            err_list = epi.loc[(check_in_range), 'orig_idx'].sort_values().unique().tolist()

            return {'Episodes': err_list}

    return error, _validate


def validate_554():
  error = ErrorDefinition(
    code = '554',
    description = 'Date of decision that the child should be placed for adoption should be on or prior to the date that the placement order was granted. [NOTE: This rule may result in false positives or false negatives if relevant episodes are in previous years; please check carefully!]',
    affected_fields = ['DATE_PLACED', 'DECOM', 'LS']
  )
  def _validate(dfs):
    if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
      return {}
    else:
      episodes = dfs['Episodes']
      placed_adoption = dfs['PlacedAdoption']

      # convert dates from string format to datetime format.
      episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
      placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y', errors='coerce')

      # Keep original index values as a column
      episodes['eps_index'] = episodes.index
      placed_adoption['pa_index'] = placed_adoption.index

      # select the first episodes with LS==E1
      e1_episodes = episodes.loc[episodes['LS']=='E1']
      first_e1_eps = e1_episodes.loc[e1_episodes.groupby('CHILD')['DECOM'].idxmin()]

      # merge
      merged = first_e1_eps.merge(placed_adoption, on='CHILD', how='left')

      # Where <LS> = 'E1' <DATE_PLACED> should be <= <DECOM> of first episode in <PERIOD_OF_CARE> with <LS> = 'E1'
      mask = merged['DATE_PLACED'] > merged['DECOM']

      # error locations
      eps_error_locs = merged.loc[mask, 'eps_index']
      pa_error_locs = merged.loc[mask, 'pa_index']

      return {'Episodes':eps_error_locs.tolist(), 'PlacedAdoption':pa_error_locs.unique().tolist()}

  return error, _validate

def validate_392A():
    error = ErrorDefinition(
        code='392A',
        description='Child is looked after but no distance is recorded. [NOTE: This check may result in false positives for children formerly UASC]',
        affected_fields=['PL_DISTANCE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            # If <LS> not = 'V3' or 'V4' and <UASC> = '0' and <COLLECTION YEAR> - 1 <UASC> = '0' and <COLLECTION YEAR> - 2 <UASC> = '0' then <PL_DISTANCE> must be provided
            epi = dfs['Episodes']
            epi['orig_idx'] = epi.index


            header = pd.DataFrame()
            if 'Header' in dfs:
                header = pd.concat((header, dfs['Header']), axis=0)
            elif 'UASC' in dfs:
                uasc = dfs['UASC']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'Header_last' in dfs:
                header = pd.concat((header, dfs['Header_last']), axis=0)
            elif 'UASC_last' in dfs:
                uasc = dfs['UASC_last']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'UASC' in header.columns:
                header = header[header.UASC == '1'].drop_duplicates('CHILD')
                epi = epi.merge(header[['CHILD', 'UASC']], how='left', on='CHILD', indicator=True)
                epi = epi[epi['_merge'] == 'left_only']
            else:
                return {}

            # Check that the episodes LS are neither V3 or V4.
            epi = epi.query("(~LS.isin(['V3','V4'])) & ( PL_DISTANCE.isna())")
            err_list = epi['orig_idx'].tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_229():
    error = ErrorDefinition(
        code = '229',
        description = "Placement provider does not match between the placing authority and the local authority code of "
                      "the provider. [NOTE: The provider's LA code is inferred from the its postcode, and may "
                      "be inaccurate in some cases.]",
        affected_fields = ['URN', 'PLACE_PROVIDER']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('provider_info' not in dfs['metadata']):
            return {}
        else:
            episodes = dfs['Episodes']
            provider_info = dfs['metadata']['provider_info']
            local_authority = dfs['metadata']['localAuthority']

            # merge
            episodes['index_eps'] = episodes.index
            episodes = episodes[episodes['URN'].notna() & (episodes['URN'] != 'XXXXXXX')]
            merged = episodes.merge(provider_info, on='URN', how='left')

            # If Ofsted URN is provided and not 'XXXXXXX' then: If <PLACE_PROVIDER> = 'PR1' then <LA> must equal Ofsted URN lookup <LA code>. If <PLACE_PROVIDER> = 'PR2' then Ofsted URN lookup <LA code> must not equal <LA>.
            mask = (
                    (merged['PLACE_PROVIDER'].eq('PR1') & merged['LA_CODE_INFERRED'].ne(local_authority))
                    | (merged['PLACE_PROVIDER'].eq('PR2') & merged['LA_CODE_INFERRED'].eq(local_authority))
            )

            eps_error_locations = merged.loc[mask, 'index_eps'].tolist()
            return {'Episodes': eps_error_locations}

    return error, _validate

# !# False negatives if child was UASC in last 2 years but data not provided
def validate_406():
    error = ErrorDefinition(
        code='406',
        description='Child is Unaccompanied Asylum-Seeking Child (UASC) or was formerly UASC. Distance should be '
                    'blank. [NOTE: This check will result in false negatives for children formerly UASC not '
                    'identified as such in loaded data]',
        affected_fields=['PL_DISTANCE'],
    )

    # If <UASC> = '1' or <COLLECTION YEAR> - 1 <UASC> = '1' or <COLLECTION YEAR> - 2 <UASC> = '1' Then
    # <PL_DISTANCE> should not be provided Note: <PL_DISTANCE> is a derived field in most instances
    def _validate(dfs):
        # Header_last also used if present
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            # Note the initial positions. Freeze a copy of the index values into a column
            epi['orig_idx'] = epi.index

            # Work out who is formerly
            header = pd.DataFrame()
            if 'Header' in dfs:
                header_current = dfs['Header']
                header = pd.concat((header, header_current), axis=0)
            elif 'UASC' in dfs:
                uasc = dfs['UASC']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'Header_last' in dfs:
                header = pd.concat((header, dfs['Header_last']), axis=0)
            elif 'UASC_last' in dfs:
                uasc = dfs['UASC_last']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'UASC' in header.columns:
                header = header[header.UASC == '1'].drop_duplicates('CHILD')
                epi = epi.merge(header[['CHILD']], how='inner', on='CHILD')
            else:
                # if theres no UASC column in header, either from XML data, inferred for CSV in ingress, or added above
                # then we can't identify anyone as UASC/formerly UASC
                return {}
            # PL_DISTANCE is added when the uploaded files are read into the tool. The code that does this is found in datastore.py

            err_list = epi.loc[epi['PL_DISTANCE'].notna(), 'orig_idx'].sort_values().unique().tolist()

            return {'Episodes': err_list}

    return error, _validate

def validate_227():
    error = ErrorDefinition(
        code='227',
        description='Ofsted Unique reference number (URN) is not valid for the episode start date.',
        affected_fields=['URN', 'DECOM']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('provider_info' not in dfs['metadata']):
            return {}
        else:
            episodes = dfs['Episodes']
            provider_info = dfs['metadata']['provider_info']

            # convert date fields from strings to datetime format. NB. REG_END is in datetime format already.
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # merge
            episodes['index_eps'] = episodes.index
            episodes = episodes[episodes['URN'].notna() & (episodes['URN'] != 'XXXXXXX')]
            merged = episodes.merge(provider_info, on='URN', how='left')
            # If <URN> provided and <URN> not = 'XXXXXXX', then if <URN> and <REG_END> are provided then <DECOM> must be before <REG_END>
            mask = merged['REG_END'].notna() & (merged['DECOM'] >= merged['REG_END'])

            eps_error_locations = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locations.tolist()}

    return error, _validate


def validate_224():
    error = ErrorDefinition(
        code='224',
        description="The Ofsted Unique reference number (URN) provided for the child's placement does not match the placement provider recorded.",
        affected_fields=['PLACE_PROVIDER']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('provider_info' not in dfs['metadata']):
            return {}
        else:
            episodes = dfs['Episodes']
            provider_info = dfs['metadata']['provider_info']

            # merge
            episodes['index_eps'] = episodes.index
            episodes = episodes[episodes['URN'].notna() & (episodes['URN'] != 'XXXXXXX')]
            episodes = episodes.merge(provider_info, on='URN', how='left', suffixes=['_eps', '_lookup'])
            # If <URN> provided and <URN> not = 'XXXXXXX', then <PLACE_PROVIDER> must = URN Lookup <PLACE_PROVIDER>
            valid = pd.Series([
                pl_pr in valid.split(',') if (pd.notna(pl_pr) and pd.notna(valid))
                else False
                for pl_pr, valid in zip(episodes['PLACE_PROVIDER'], episodes['PROVIDER_CODES'])
            ])
            eps_error_locations = episodes.loc[~valid, 'index_eps']
            return {'Episodes': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_221():
    error = ErrorDefinition(
        code='221',
        description="The Ofsted Unique reference number (URN) provided for the child's placement does not match the placement postcode provided.",
        affected_fields=['PL_POST']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('provider_info' not in dfs['metadata']):
            return {}
        else:
            episodes = dfs['Episodes']
            provider_info = dfs['metadata']['provider_info']
            ls_list = ['V3', 'V4']
            place_list = ['K1', 'K2', 'R3', 'S1']
            xxx = 'X' * 7
            # merge
            episodes['index_eps'] = episodes.index
            episodes = episodes[
                episodes['URN'].notna()
                & (episodes['URN'] != xxx)
                & (~episodes['LS'].isin(ls_list))
                & episodes['PLACE'].isin(place_list)
                & episodes['PL_POST'].notna()
                ]
            merged = episodes.merge(provider_info, on='URN', how='left')
            # If <URN> provided and <URN> not = 'XXXXXX', and <LS> not = 'V3', 'V4' and where <PL> = 'K1', 'K2', 'R3' or 'S1' and <PL_POST> provided, <PL_POST> should = URN Lookup <Provider Postcode>
            mask = merged['PL_POST'].str.replace(' ', '') != merged['POSTCODE']

            eps_error_locations = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locations.unique().tolist()}

    return error, _validate


def validate_228():
    error = ErrorDefinition(
        code='228',
        description='Ofsted Unique reference number (URN) is not valid for the episode end date '
                    '[NOTE: may give false positives on open episodes at providers who close during the year]',
        affected_fields=['URN', 'DEC']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('provider_info' not in dfs['metadata']):
            return {}
        else:
            episodes = dfs['Episodes']
            provider_info = dfs['metadata']['provider_info']
            collection_end = dfs['metadata']['collection_end']

            # convert date fields from strings to datetime format. NB. REG_END is in datetime format already.
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # merge
            episodes['index_eps'] = episodes.index
            episodes = episodes[episodes['URN'].notna() & (episodes['URN'] != 'XXXXXXX')]
            provider_info = provider_info[provider_info['REG_END'].notna()]

            merged = episodes.merge(provider_info, on='URN', how='inner')
            # If <URN> provided and not = 'XXXXXXX', and Ofsted URN <REG_END> not NULL then <DEC> if provided
            # must be <= Ofsted <REG_END>OR if not provided then<COLLECTION_END_DATE>must be<= <REG_END>.
            # Note: For open episodes (those without an end date) a check should be made to ensure that the Ofsted
            # URN was still open at the 31 March of the current year.
            mask = (
                    (merged['DEC'].notna() & (merged['DEC'] > merged['REG_END']))
                    | (merged['DEC'].isna() & (collection_end > merged['REG_END']))
            )

            eps_error_locations = merged.loc[mask, 'index_eps'].sort_values().to_list()
            return {'Episodes': eps_error_locations}

    return error, _validate


def validate_219():
    error = ErrorDefinition(
        code='219',
        description="The Ofsted Unique reference number (URN) provided for the child's placement does not match the placement type recorded.",
        affected_fields=['URN', 'PLACE']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('provider_info' not in dfs['metadata']):
            return {}
        else:
            episodes = dfs['Episodes']
            provider_info = dfs['metadata']['provider_info']

            # merge
            episodes['index_eps'] = episodes.index
            episodes = episodes[episodes['URN'].notna() & (episodes['URN'] != 'XXXXXXX')]
            episodes = episodes.merge(provider_info, on='URN', how='left')
            # If <URN> provided and <URN> not = 'XXXXXXX' then <PL> must = any URN Lookup <PLACEMENT CODE> of matching URN Lookup <URN>
            place_valid = pd.Series([
                False if (pd.isna(pl) or pd.isna(valid)) else pl in valid.split(',')
                for pl, valid in zip(episodes['PLACE'], episodes['PLACE_CODES'])
            ])

            eps_error_locations = episodes.loc[~place_valid, 'index_eps']
            return {'Episodes': eps_error_locations.tolist()}

    return error, _validate


def validate_1008():
    error = ErrorDefinition(
        code='1008',
        description='Ofsted Unique Reference Number (URN) is not valid.',
        affected_fields=['URN']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'provider_info' not in dfs['metadata']:
            return {}
        else:
            episodes = dfs['Episodes']
            providers = dfs['metadata']['provider_info']

            episodes['index_eps'] = episodes.index
            episodes = episodes[episodes['URN'].notna() & (episodes['URN'] != 'XXXXXXX')].copy()
            episodes['URN'] = episodes['URN'].astype(str)
            episodes = episodes.merge(providers, on='URN', how='left', indicator=True)
            mask = episodes['_merge'] == 'left_only'
            eps_error_locations = episodes.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locations.tolist()}

    return error, _validate


def validate_218():
    error = ErrorDefinition(
        code='218',
        description='Ofsted Unique reference number (URN) is required.',
        affected_fields=['URN']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            collection_start = dfs['metadata']['collection_start']
            pl_list = ['H5', 'P1', 'P2', 'P3', 'R1', 'R2', 'R5', 'T0', 'T1', 'T2', 'T3', 'T4', 'Z1']

            # convert string date values to datetime format to enable comparison.
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            episodes['DEC_dt'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            out_of_england = episodes['PL_LA'].astype('str').str.upper().str.startswith(('N', 'W', 'S', 'C'))
            place_exempt = episodes['PLACE'].isin(pl_list)
            ends_after_collection_start = (episodes['DEC_dt'] >= collection_start) | episodes['DEC'].isna()

            mask = ends_after_collection_start & episodes['URN'].isna() & ~place_exempt & ~out_of_england

            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.tolist()}

    return error, _validate


def validate_546():
    error = ErrorDefinition(
        code='546',
        description='Children aged 5 or over at 31 March should not have health promotion information completed.',
        affected_fields=['DOB', 'HEALTH_CHECK']
    )

    def _validate(dfs):
        if 'OC2' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            collection_end = dfs['metadata']['collection_end']
            # add CLA column
            oc2 = add_CLA_column(dfs, 'OC2')

            # to datetime
            oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # If <DOB> >= 5 years prior to<COLLECTION_END_DATE>and<CONTINUOUSLY_LOOKED_AFTER>= 'Y' then<HEALTH_CHECK>` should not be provided
            mask = (collection_end >= (oc2['DOB'] + pd.offsets.DateOffset(years=5))) & oc2[
                'CONTINUOUSLY_LOOKED_AFTER'] & oc2['HEALTH_CHECK'].notna()
            error_locations = oc2.index[mask]
            return {'OC2': error_locations.tolist()}

    return error, _validate


def validate_545():
    error = ErrorDefinition(
        code='545',
        description='Child is aged under 5 at 31 March and has been looked after continuously for 12 months yet health promotion information has not been completed.',
        affected_fields=['DOB', 'HEALTH_CHECK'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            collection_end = dfs['metadata']['collection_end']
            # add CLA column
            oc2 = add_CLA_column(dfs, 'OC2')

            # to datetime
            oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # If <DOB> < 5 years prior to <COLLECTION_END_DATE>and<CONTINUOUSLY_LOOKED_AFTER>= 'Y' then<HEALTH_CHECK>` should be provided.
            mask = (collection_end < (oc2['DOB'] + pd.offsets.DateOffset(years=5))) & oc2['CONTINUOUSLY_LOOKED_AFTER'] & \
                   oc2['HEALTH_CHECK'].isna()
            error_locations = oc2.index[mask]
            return {'OC2': error_locations.tolist()}

    return error, _validate


def validate_543():
    error = ErrorDefinition(
        code='543',
        description='Child is aged 10 or over at 31 March and has been looked after continuously for 12 months yet conviction information has not been completed.',
        affected_fields=['DOB', 'CONVICTED']
    )

    def _validate(dfs):
        if 'OC2' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            collection_end = dfs['metadata']['collection_end']
            # add CLA column
            oc2 = add_CLA_column(dfs, 'OC2')

            # to datetime
            oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # If <DOB> >= 10 years prior to <COLLECTION_END_DATE>and<CONTINUOUSLY_LOOKED_AFTER> = 'Y' then <CONVICTED> should be provided
            mask = (collection_end > (oc2['DOB'] + pd.offsets.DateOffset(years=10))) & oc2[
                'CONTINUOUSLY_LOOKED_AFTER'] & oc2['CONVICTED'].isna()
            error_locations = oc2.index[mask]
            return {'OC2': error_locations.tolist()}

    return error, _validate


def validate_560():
    error = ErrorDefinition(
        code='560',
        description='Date of decision that the child should be placed for adoption this year is different from that recorded last year but the decision to place the child for adoption did not change.',
        affected_fields=['DATE_PLACED', 'DATE_PLACED_CEASED']
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs or 'PlacedAdoption_last' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            pa_last = dfs['PlacedAdoption_last']

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            pa_last.reset_index(inplace=True)
            merged = placed_adoption.merge(pa_last, how='inner', on='CHILD', suffixes=['_now', '_last'])

            # If <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED> has been provided and <DATE_PLACED_CEASED> is Null then <CURRENT_COLLECTION_YEAR> <DATE_PLACED> should = <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED>
            mask = (
                    merged['DATE_PLACED_last'].notna()
                    & merged['DATE_PLACED_CEASED_last'].isna()
                    & (merged['DATE_PLACED_now'] != merged['DATE_PLACED_last'])
            )
            # error locations
            error_locs = merged.loc[mask, 'index_now']
            return {'PlacedAdoption': error_locs.tolist()}

    return error, _validate


def validate_561():
    error = ErrorDefinition(
        code='561',
        description='Date of the decision that the child should be placed for adoption this year is the same as that recorded last year but records show that the decision changed, and the child should no longer be placed for adoption last year.',
        affected_fields=['DATE_PLACED']
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs or 'PlacedAdoption_last' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            pa_last = dfs['PlacedAdoption_last']

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            pa_last.reset_index(inplace=True)
            merged = placed_adoption.merge(pa_last, how='inner', on='CHILD', suffixes=['_now', '_last'])

            # If <CURRENT_COLLECTION_YEAR> <DATE_PLACED> is = <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED> then <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED_CEASED> and <REASON_PLACED_CEASED> should be Null
            mask = (
                    (merged['DATE_PLACED_now'] == merged['DATE_PLACED_last'])
                    & merged[['REASON_PLACED_CEASED_last', 'DATE_PLACED_CEASED_last']].notna().any(axis=1)
            )

            # error locations
            error_locs = merged.loc[mask, 'index_now']
            return {'PlacedAdoption': error_locs.tolist()}

    return error, _validate


def validate_601():
    error = ErrorDefinition(
        code='601',
        description='The additional fields relating to adoption have not been completed although the episode data shows that the child was adopted during the year.',
        affected_fields=['REC', 'DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            episodes = dfs['Episodes']
            collection_start = dfs['metadata']['collection_start']
            collection_end = dfs['metadata']['collection_end']

            # prepare to merge
            ad1.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            # only keep episodes with adoption RECs during year
            adoption_eps_mask = (
                    (episodes['DEC'] >= collection_start)
                    & (episodes['DEC'] <= collection_end)
                    & episodes['REC'].isin(['E11', 'E12'])
            )
            episodes = episodes[adoption_eps_mask]

            # inner merge to take only episodes of children which are also found in the ad1 table
            merged = episodes.merge(ad1, on='CHILD', how='inner', suffixes=['_eps', '_ad1'])

            some_absent = (
                merged[['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']]
                    .isna()
                    .any(axis=1)
            )

            error_locs_ad1 = merged.loc[some_absent, 'index_ad1'].unique().tolist()
            error_locs_eps = merged.loc[some_absent, 'index_eps'].unique().tolist()

            return {'AD1': error_locs_ad1,
                    'Episodes': error_locs_eps}

    return error, _validate


def validate_302():
    error = ErrorDefinition(
        code='302',
        description='First episode starts before child was born.',
        affected_fields=['DECOM', 'DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            episodes = episodes.reset_index()
            header = header.reset_index()

            episodes = episodes.loc[episodes.groupby('CHILD')['DECOM'].idxmin()]

            merged = episodes.merge(header, how='left', on=['CHILD'], suffixes=('_eps', '_hdr'))

            # omitting looking for the 'S' episode as we may not have it in current year's data
            # care_start = merged['RNE'].str.upper().astype(str).isin(['S'])

            started_before_born = merged['DOB'] > merged['DECOM']

            eps_errors = merged.loc[started_before_born, 'index_eps'].to_list()
            hdr_errors = merged.loc[started_before_born, 'index_hdr'].to_list()
            return {'Episodes': eps_errors,
                    'Header': hdr_errors}

    return error, _validate


def validate_434():
    error = ErrorDefinition(
        code='434',
        description="Reason for new episode is that child's legal status has changed but not the placement, but this is not reflected in the episode data.",
        affected_fields=['RNE', 'LS', 'PLACE', 'PL_POST', 'URN', 'PLACE_PROVIDER']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            # create columns of previous values

            cols = ['PLACE', 'PL_POST', 'URN', 'PLACE_PROVIDER']

            episodes = episodes.sort_values(['CHILD', 'DECOM'])

            error_mask = (
                    (episodes['CHILD'] == episodes['CHILD'].shift(1))
                    & (episodes['RNE'] == 'L')
                    & (
                            (episodes['LS'] == episodes['LS'].shift(1))
                            | (episodes[cols].fillna('') != episodes[cols].shift(1).fillna('')).any(axis=1)
                    )
            )
            # error locations
            error_locs = episodes.index[error_mask].to_list()
            return {'Episodes': error_locs}

    return error, _validate


def validate_336():
    error = ErrorDefinition(
        code='336',
        description='Child does not have a foster placement immediately prior to being placed for adoption.',
        affected_fields=['PLACE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            place_code_list = ['A3', 'A4']
            prev_code_list = ['A3', 'A4', 'A5', 'A6', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            # new column that contains place of previous episode

            sorted_and_grouped_eps = (episodes
                                      .sort_values('DECOM')
                                      .groupby('CHILD'))

            episodes['PLACE_prev'] = sorted_and_grouped_eps['PLACE'].shift(1)
            episodes['is_first_episode'] = False
            episodes.loc[sorted_and_grouped_eps['DECOM'].idxmin(), 'is_first_episode'] = True

            # Where <PL> = 'A3' or 'A5' previous episode <PL> must be one of:
            # ('A3'; 'A4'; 'A5'; 'A6'; 'U1', 'U2', 'U3', 'U4', 'U5' or 'U6')
            mask = (
                    (episodes['PLACE'].isin(place_code_list))
                    & ~episodes['PLACE_prev'].isin(prev_code_list)
                    & ~episodes['is_first_episode']  # omit first eps, as prev_PLACE is NaN
            )

            # error locations
            error_locs = episodes.index[mask]
            return {'Episodes': error_locs.tolist()}

    return error, _validate


def validate_105():
    error = ErrorDefinition(
        code='105',
        description='Data entry for Unaccompanied Asylum-Seeking Children (UASC) status of child is invalid or has not been completed.',
        affected_fields=['UASC']
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            try:
                file_format = dfs['metadata']['file_format']
            except KeyError as e:
                raise MissingMetadataError(*e.args)
            if file_format == 'csv':
                return {}

            header = dfs['Header']
            code_list = [0, 1]

            mask = ~pd.to_numeric(header['UASC'], errors='coerce').isin(code_list)
            error_locs = header.index[mask]

            return {'Header': error_locs.tolist()}

    return error, _validate


def validate_1003():
    error = ErrorDefinition(
        code='1003',
        description="Date of LA's decision that a child should be placed for adoption is before the child started to be looked after.",
        affected_fields=['DATE_PLACED', 'DECOM', 'RNE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placed_adoption = dfs['PlacedAdoption']

            # to datetime
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # select the earliest episodes with RNE =  S
            eps_rne = episodes[episodes['RNE'] == 'S']
            first_eps_idxs = eps_rne.groupby('CHILD')['DECOM'].idxmin()
            first_eps = eps_rne.loc[first_eps_idxs]
            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            first_eps.reset_index(inplace=True)
            merged = first_eps.merge(placed_adoption, how='left', on='CHILD', suffixes=['_eps', '_pa'])

            # <DATE_PLACED> cannot be prior to <DECOM> of the first episode with <RNE> = 'S'
            mask = merged['DATE_PLACED'] < merged['DECOM']
            eps_error_locs = merged.loc[mask, 'index_eps']
            pa_error_locs = merged.loc[mask, 'index_pa']
            return {'Episodes': eps_error_locs.tolist(), 'PlacedAdoption': pa_error_locs.tolist()}

    return error, _validate


def validate_334():
    error = ErrorDefinition(
        code='334',
        description="Date child started to be looked after in latest period of care must be on or prior to the date should be placed for adoption. ",
        affected_fields=['DATE_INT', 'DECOM', 'RNE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            ad1 = dfs['AD1']

            # to datetime
            ad1['DATE_INT'] = pd.to_datetime(ad1['DATE_INT'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # select the earliest episodes with RNE =  S
            eps_rne = episodes[episodes['RNE'] == 'S']
            last_eps_idxs = eps_rne.groupby('CHILD')['DECOM'].idxmax()
            last_eps = eps_rne.loc[last_eps_idxs]

            # prepare to merge
            ad1.reset_index(inplace=True)
            last_eps.reset_index(inplace=True)
            merged = last_eps.merge(ad1, how='left', on='CHILD', suffixes=['_eps', '_ad1'])

            # <DATE_PLACED> cannot be prior to <DECOM> of the first episode with <RNE> = 'S'
            mask = merged['DATE_INT'] < merged['DECOM']

            eps_error_locs = merged.loc[mask, 'index_eps']
            ad1_error_locs = merged.loc[mask, 'index_ad1']

            return {'Episodes': eps_error_locs.tolist(),
                    'AD1': ad1_error_locs.tolist()}

    return error, _validate


def validate_559():
    error = ErrorDefinition(
        code='559',
        description='Date of decision that a child should be placed for adoption was not in the current year but the date of the decision that the child should be placed for adoption was not completed in a previous return.',
        affected_fields=['DATE_PLACED']
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs or 'PlacedAdoption_last' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            pa_last = dfs['PlacedAdoption_last']
            collection_start = dfs['metadata']['collection_start']

            # convert dates to appropriate format
            pa_last['DATE_PLACED'] = pd.to_datetime(pa_last['DATE_PLACED'], format='%d/%m/%Y', errors='coerce')
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            pa_last.reset_index(inplace=True)
            merged = placed_adoption.merge(pa_last, how='left', on='CHILD', suffixes=['_now', '_last'])

            # If <DATE_PLACED> < <COLLECTION_START_DATE> then <CURRENT_COLLECTION_YEAR> -1 <DATE_PLACED> cannot be Null
            mask = (merged['DATE_PLACED_now'] < collection_start) & merged['DATE_PLACED_last'].isna()
            # error locations
            error_locs = merged.loc[mask, 'index_now']
            return {'PlacedAdoption': error_locs.tolist()}

    return error, _validate


def validate_521():
    error = ErrorDefinition(
        code='521',
        description="Date of local authority's decision (LA) that adoption is in the best interests of the child (date should be placed) must be on or prior to the date the child is placed for adoption.",
        affected_fields=['PLACE', 'DECOM', 'DATE_INT']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            ad1 = dfs['AD1']
            code_list = ['A3', 'A4', 'A5', 'A6']
            # if PLACE is equal to A3, A4, A5 or A6 then placed-for-adoption = Y

            # to datetime
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            ad1['DATE_INT'] = pd.to_datetime(ad1['DATE_INT'], format='%d/%m/%Y', errors='coerce')

            # prepare to merge
            episodes.reset_index(inplace=True)
            ad1.reset_index(inplace=True)
            merged = episodes.merge(ad1, how='left', on='CHILD', suffixes=['_eps', '_ad1'])

            # <DATE_INT> must be <= <DECOM> where <PLACED_FOR_ADOPTION> = 'Y'
            mask = merged['PLACE'].isin(code_list) & (merged['DATE_INT'] > merged['DECOM'])
            # error locations
            ad1_error_locs = merged.loc[mask, 'index_ad1']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locs.tolist(), 'AD1': ad1_error_locs.tolist()}

    return error, _validate


# !# potential false negatives, as this only operates on current and previous year data
def validate_1000():
    error = ErrorDefinition(
        code='1000',
        description='This child is recorded as having died in care and therefore should not have the care leaver information completed. [NOTE: This only tests the current and previous year data loaded into the tool]',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC3' not in dfs:
            return {}

        else:
            episodes = dfs['Episodes']
            oc3 = dfs['OC3']

            episodes_ended_e2 = episodes['REC'].str.upper().astype(str).isin(['E2'])
            episodes = episodes.loc[episodes_ended_e2]

            if 'Episodes_last' in dfs:
                episodes_last = dfs['Episodes_last']
                episodes_last_ended_e2 = episodes_last['REC'].str.upper().astype(str).isin(['E2'])
                episodes_last = episodes_last.loc[episodes_last_ended_e2]
                has_previous_e2 = oc3['CHILD'].isin(episodes_last['CHILD'])
                has_current_e2 = oc3['CHILD'].isin(episodes['CHILD'])
                error_mask = has_current_e2 | has_previous_e2
            else:
                has_current_e2 = oc3['CHILD'].isin(episodes['CHILD'])
                error_mask = has_current_e2

            validation_error_locations = oc3.index[error_mask]

            return {'OC3': validation_error_locations.tolist()}

    return error, _validate


def validate_579():
    error = ErrorDefinition(
        code='579',
        description='A new decision that the child should be placed for adoption this year cannot start when the previous decision is still open. Decisions to place the child for adoption should also not overlap. The date of any new decision to place the child for adoption must not be before the date placed ceased of previous decisions.',
        affected_fields=['DATE_PLACED', 'DATE_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:

            adopt_placed = dfs['PlacedAdoption']
            adopt_placed['DATE_PLACED'] = pd.to_datetime(adopt_placed['DATE_PLACED'], format='%d/%m/%Y',
                                                         errors='coerce')
            adopt_placed['DATE_PLACED_CEASED'] = pd.to_datetime(adopt_placed['DATE_PLACED_CEASED'], format='%d/%m/%Y',
                                                                errors='coerce')

            adopt_placed.sort_values(['CHILD', 'DATE_PLACED'], inplace=True)

            adopt_placed.reset_index(inplace=True)
            adopt_placed.reset_index(inplace=True)  # Twice on purpose

            adopt_placed['LAG_INDEX'] = adopt_placed['level_0'].shift(-1)

            lag_adopt_placed = adopt_placed.merge(adopt_placed, how='inner', left_on='level_0', right_on='LAG_INDEX',
                                                  suffixes=['', '_PREV'])

            # We're only interested in cases where there is more than one row for a child.
            lag_adopt_placed = lag_adopt_placed[lag_adopt_placed['CHILD'] == lag_adopt_placed['CHILD_PREV']]

            # A previous ADOPT_PLACED_CEASED date is null
            mask1 = lag_adopt_placed['DATE_PLACED_CEASED_PREV'].isna()
            # ADOPT_PLACED is before previous ADOPT_PLACED (overlapping dates)
            mask2 = lag_adopt_placed['DATE_PLACED'] < lag_adopt_placed['DATE_PLACED_CEASED_PREV']

            mask = mask1 | mask2

            error_list = lag_adopt_placed['index'][mask].to_list()
            error_list.sort()
            return {'PlacedAdoption': error_list}

    return error, _validate


def validate_351():
    error = ErrorDefinition(
        code='351',
        description='Child was over 21 at the start of the current collection year.',
        affected_fields=['DOB', ]
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}

        else:
            header = dfs['Header']
            collection_start = dfs['metadata']['collection_start']

            # Convert from string to date to appropriate format
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')

            mask = collection_start > (header['DOB'] + pd.DateOffset(years=21))
            # error locations
            header_error_locs = header.index[mask]

            return {'Header': header_error_locs.tolist()}

    return error, _validate


def validate_301():
    error = ErrorDefinition(
        code='301',
        description='Date of birth falls after the year ended.',
        affected_fields=['DOB']
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            collection_end = dfs['metadata']['collection_end']

            # convert dates
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')

            # <DOB> must be <= <COLLECTION_END_DATE>
            mask = header['DOB'] > collection_end

            # error locations
            error_locs = header.index[mask]
            return {'Header': error_locs.tolist()}

    return error, _validate


def validate_577():
    error = ErrorDefinition(
        code='577',
        description='Child ceased to be looked after but there is a missing/away from placement without authorisation period without an end date.',
        affected_fields=['MIS_END']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            missing = dfs['Missing']

            episodes['original_index'] = episodes.index

            # put dates in appropriate format.
            missing['MIS_END'] = pd.to_datetime(missing['MIS_END'], format='%d/%m/%Y', errors='coerce')
            missing['MIS_START'] = pd.to_datetime(missing['MIS_START'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # filter data based on provided conditions.
            missing = missing[missing['MIS_START'].notna()].copy()
            episodes = episodes.dropna(subset=['DECOM'])

            # create period of care blocks
            episodes = episodes.sort_values(['CHILD', 'DECOM'])

            episodes['index'] = pd.RangeIndex(0, len(episodes))
            episodes['index+1'] = episodes['index'] + 1
            episodes = episodes.merge(episodes, left_on='index', right_on='index+1',
                                  how='left', suffixes=[None, '_prev'])
            episodes = episodes[['original_index', 'DECOM', 'DEC', 'DEC_prev', 'CHILD', 'CHILD_prev', 'LS']]

            episodes['new_period'] = (
                (episodes['DECOM'] > episodes['DEC_prev'])
                | (episodes['CHILD'] != episodes['CHILD_prev'])
            )
            episodes['period_id'] = episodes['new_period'].astype(int).cumsum()

            # allocate the same DECOM (min) and DEC (max) to all episodes in a period of care.
            pocs = pd.DataFrame()
            pocs[['CHILD', 'poc_DECOM']] = episodes.groupby('period_id')[['CHILD', 'DECOM']].first()
            pocs['poc_DEC'] = episodes.groupby('period_id')['DEC'].nth(-1)

            # prepare to merge
            missing['index_ing'] = missing.index

            pocs = pocs.merge(missing, on='CHILD', how='right', suffixes=['_eps', '_ing'])
            # poc : period of care
            pocs['out_of_poc'] = (
                # (a) POC is over, but Missing ep is ongoing:
                (pocs['MIS_START'].notna() & pocs['MIS_END'].isna() & pocs['poc_DEC'].notna())
                # (b) Ongoing Missing ep, but started before POC:
                | (pocs['MIS_END'].isna() & (pocs['MIS_START'] < pocs['poc_DECOM']))
                # (c) Missing ep ends after POC:
                | (pocs['MIS_END'] > pocs['poc_DEC'])
                # (d) Missing ep ends before POC:
                | (pocs['MIS_END'] < pocs['poc_DECOM'])
                # (e?) Starts during a previous poc??? (row 12 of Missing table in test_validate_577)
            )

            # Drop rows where child was not present in 'Missing' table.
            pocs = pocs[pocs['index_ing'].notna()]

            mask = pocs.groupby('index_ing')['out_of_poc'].transform('min')
            miss_error_locs = pocs.loc[mask, 'index_ing'].astype(int).unique().tolist()

            return {'Missing': miss_error_locs}

    return error, _validate


def validate_460():
    error = ErrorDefinition(
        code='460',
        description='Reason episode ceased is that child stayed with current carers at age 18 (or above), but child is aged under 18.',
        affected_fields=['DEC', 'REC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB18'] = header['DOB'] + pd.DateOffset(years=18)

            episodes = episodes[episodes['REC'] == 'E17']

            episodes_merged = episodes.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                           indicator=True).set_index('index')

            care_ended_under_18 = episodes_merged['DOB18'] > episodes_merged['DEC']

            error_mask = care_ended_under_18

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_578():
    error = ErrorDefinition(
        code='578',
        description='The date that the child started to be missing is after the child ceased to be looked after.',
        affected_fields=['MIS_START']
    )

    def _validate(dfs):

        if 'Episodes' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            missing = dfs['Missing']

            episodes['original_index'] = episodes.index

            # convert dates
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            missing['MIS_START'] = pd.to_datetime(missing['MIS_START'], format='%d/%m/%Y', errors='coerce')

            # create period of care blocks
            episodes = episodes.sort_values(['CHILD', 'DECOM'])
            episodes = episodes.dropna(subset=['DECOM'])

            episodes['index'] = pd.RangeIndex(0, len(episodes))
            episodes['index+1'] = episodes['index'] + 1
            episodes = episodes.merge(episodes, left_on='index', right_on='index+1',
                                  how='left', suffixes=[None, '_prev'])
            episodes = episodes[['original_index', 'DECOM', 'DEC', 'DEC_prev', 'CHILD', 'CHILD_prev', 'LS']]

            episodes['new_period'] = (
                    (episodes['DECOM'] > episodes['DEC_prev'])
                    | (episodes['CHILD'] != episodes['CHILD_prev'])
            )
            episodes['period_id'] = episodes['new_period'].astype(int).cumsum()

            # allocate the same DECOM (min) and DEC (max) to all episodes in a period of care.
            episodes['poc_DECOM'] = episodes.groupby('period_id')['DECOM'].transform('min')
            episodes['poc_DEC'] = episodes.groupby('period_id')['DEC'].transform('max')

            # prepare to merge
            missing['index_ing'] = missing.index

            pocs = pd.DataFrame()
            pocs[['CHILD', 'poc_DECOM']] = episodes.groupby('period_id')[['CHILD', 'DECOM']].first()
            pocs['poc_DEC'] = episodes.groupby('period_id')['DEC'].nth(-1)

            pocs = pocs.merge(missing, on='CHILD', how='right', suffixes=['_eps', '_ing'])
            # If <MIS_START> >=DEC, then no missing/away from placement information should be recorded
            pocs['out_of_poc'] = (
                (pocs['MIS_START'] < pocs['poc_DECOM'])
                | ((pocs['MIS_START'] > pocs['poc_DEC']) & pocs['poc_DEC'].notna())
            )

            # Drop rows where child was not present in 'Missing' table.
            pocs = pocs[pocs['index_ing'].notna()]

            mask = pocs.groupby('index_ing')['out_of_poc'].transform('min')
            miss_error_locs = pocs.loc[mask, 'index_ing'].astype(int).unique().tolist()

            # In this case it is not necessary to flag the DEC or DECOM that value because that same DEC or DECOM value might have passed with other values of MIS_START. Flagging the DECOM/ DEC value is not specific enough to be helpful to the user.
            return {'Missing': miss_error_locs}

    return error, _validate


def validate_391():
    error = ErrorDefinition(
        code='391',
        description='Young person was not 17, 18, 19, 20 or 21 during the current collection year. ',
        affected_fields=['DOB', 'IN_TOUCH', 'ACTIV', 'ACCOM']
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            collection_end = dfs['metadata']['collection_end']

            # convert dates to datetime format
            oc3['DOB'] = pd.to_datetime(oc3['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # If <DOB> < 17 years prior to <COLLECTION_END_DATE> then <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
            check_age = (oc3['DOB'] + pd.offsets.DateOffset(years=17) > collection_end)
            mask = check_age & (oc3['IN_TOUCH'].notna() | oc3['ACTIV'].notna() | oc3['ACCOM'].notna())
            # Then raise an error if either IN_TOUCH, ACTIV, or ACCOM have been provided too

            # error locations
            oc3_error_locs = oc3.index[mask]

            return {'OC3': oc3_error_locs.tolist()}

    return error, _validate


def validate_632():
    error = ErrorDefinition(
        code='632',
        description='Date of previous permanence order not a valid value. NOTE: This rule may result in false negatives where the period of care started before the current collection year',
        affected_fields=['DATE_PERM', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PrevPerm' not in dfs:
            return {}
        else:

            # function to check that date is of the right format
            def valid_date(dte):
                try:
                    lst = dte.split('/')
                except AttributeError:
                    return pd.NaT
                # Preceding block checks for the scenario where the value passed in is nan/naT

                # date should have three elements
                if (len(lst) != 3):
                    return pd.NaT

                z_list = ['ZZ', 'ZZ', 'ZZZZ']
                # We set the date to the latest possible value to avoid false positives
                offset_list = [pd.DateOffset(months=1, days=-1),
                               pd.DateOffset(years=1, days=-1),
                               None]
                # that is, go to the next month/year and take the day before that
                already_found_non_zeds = False
                date_bits = []

                for i, zeds, offset in zip(lst, z_list, offset_list):
                    if i == zeds:
                        # I'm assuming it is invalid to have a date like '01/ZZ/ZZZZ'
                        if already_found_non_zeds:
                            return pd.NaT
                        # Replace day & month zeds with '01' so we can check if the resulting date is valid
                        # and set the offset so we can compare the latest corresponding date
                        elif i == 'ZZ':
                            i = '01'
                            offset_to_use = offset
                    else:
                        already_found_non_zeds = True
                    date_bits.append(i)

                as_datetime = pd.to_datetime('/'.join(date_bits),
                                             format='%d/%m/%Y', errors='coerce')
                try:
                    as_datetime += offset_to_use
                except NameError:  # offset_to_use only defined if needed
                    pass
                return as_datetime

            episodes = dfs['Episodes']
            prevperm = dfs['PrevPerm']

            # convert dates from strings to appropriate format.
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            prevperm['DATE_PERM_dt'] = prevperm['DATE_PERM'].apply(valid_date)

            # select first episodes
            first_eps_idxs = episodes.groupby('CHILD')['DECOM'].idxmin()
            first_eps = episodes[episodes.index.isin(first_eps_idxs)]

            # prepare to merge
            first_eps.reset_index(inplace=True)
            prevperm.reset_index(inplace=True)
            merged = first_eps.merge(prevperm, on='CHILD', how='left', suffixes=['_eps', '_prev'])

            # If provided <DATE_PERM> should be prior to <DECOM> and in a valid format and contain a valid date Format should be DD/MM/YYYY or one or more elements of the date can be replaced by ZZ if part of the date element is not known.
            mask = (merged['DATE_PERM_dt'] >= merged['DECOM']) | (merged['DATE_PERM'].notna()
                                                                  & merged['DATE_PERM_dt'].isna()
                                                                  & (merged['DATE_PERM'] != 'ZZ/ZZ/ZZZZ')
                                                                  )

            # error locations
            prev_error_locs = merged.loc[mask, 'index_prev']
            eps_error_locs = merged.loc[mask, 'index_eps']

            return {'Episodes': eps_error_locs.tolist(), 'PrevPerm': prev_error_locs.unique().tolist()}

    return error, _validate


def validate_165():
    error = ErrorDefinition(
        code='165',
        description='Data entry for mother status is invalid.',
        affected_fields=['MOTHER', 'SEX', 'ACTIV', 'ACCOM', 'IN_TOUCH', 'DECOM']
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']
            oc3 = dfs['OC3']
            collection_start = dfs['metadata']['collection_start']
            collection_end = dfs['metadata']['collection_end']
            valid_values = ['0', '1']

            # prepare to merge
            oc3.reset_index(inplace=True)
            header.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            # Drop all episodes with V3/V4 legal status
            v3v4_ls = episodes['LS'].str.upper().isin(['V3', 'V4'])
            index_v3v4_ls = episodes.loc[v3v4_ls].index
            episodes.drop(index_v3v4_ls, inplace=True)

            # fill in missing DECs with the collection year end date
            missing_last_DECs = (
                episodes['DEC'].isna()
            )
            episodes.loc[missing_last_DECs, 'DEC'] = collection_end

            episodes['EPS'] = (episodes['DEC'] >= collection_start) & (episodes['DECOM'] <= collection_end)
            episodes['EPS_COUNT'] = episodes.groupby('CHILD')['EPS'].transform('sum')

            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er']).merge(oc3, on='CHILD',
                                                                                                    how='left')

            # Raise error if provided <MOTHER> is not a valid value
            value_validity = merged['MOTHER'].notna() & (~merged['MOTHER'].astype(str).isin(valid_values))

            # Raise error if provided <MOTHER> and child is male
            male = merged['MOTHER'].notna() & (merged['SEX'].astype(str) == '1')

            # Raise error if female and not provided
            female = (merged['SEX'].astype(str) == '2')
            has_mother = merged['MOTHER'].notna()
            eps_in_year = (merged['EPS_COUNT'] > 0)
            has_oc3 = (merged['ACTIV'].notna() | merged['ACCOM'].notna() | merged['IN_TOUCH'].notna())

            # If provided <MOTHER> must be a valid value (and child must be female). If not provided <MOTHER> then either <GENDER> is male or no episode record for current year and any of <IN_TOUCH>, <ACTIV> or <ACCOM> have been provided
            mask = value_validity | male | (~has_mother & female & eps_in_year) | (
                    has_mother & female & ~eps_in_year & has_oc3)

            # That is, if value not provided and child is a female with eps in current year or no values of IN_TOUCH, ACTIV and ACCOM, then raise error.
            error_locs_eps = merged.loc[mask, 'index_eps']
            error_locs_header = merged.loc[mask, 'index_er']
            error_locs_oc3 = merged.loc[mask, 'index']

            return {'Header': error_locs_header.dropna().unique().tolist(),
                    'OC3': error_locs_oc3.dropna().unique().tolist()}

    return error, _validate


def validate_1014():
    error = ErrorDefinition(
        code='1014',
        description='UASC information is not required for care leavers',
        affected_fields=['ACTIV', 'ACCOM', 'IN_TOUCH', 'DUC']
    )

    def _validate(dfs):
        if 'UASC' not in dfs or 'Episodes' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            uasc = dfs['UASC']
            episodes = dfs['Episodes']
            oc3 = dfs['OC3']
            collection_start = dfs['metadata']['collection_start']
            collection_end = dfs['metadata']['collection_end']

            # prepare to merge
            oc3.reset_index(inplace=True)
            uasc.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            date_check = (
                    ((episodes['DEC'] >= collection_start) & (episodes['DECOM'] <= collection_end))
                    | ((episodes['DECOM'] <= collection_end) & episodes['DEC'].isna())
            )
            episodes['EPS'] = date_check
            episodes['EPS_COUNT'] = episodes.groupby('CHILD')['EPS'].transform('sum')

            # inner merge to take only episodes of children which are also found on the uasc table
            merged = episodes.merge(uasc, on='CHILD', how='inner', suffixes=['_eps', '_sc']).merge(oc3, on='CHILD',
                                                                                                   how='left')
            # adding suffixes with the secondary merge here does not go so well yet.

            some_provided = (merged['ACTIV'].notna() | merged['ACCOM'].notna() | merged['IN_TOUCH'].notna())

            mask = (merged['EPS_COUNT'] == 0) & some_provided

            error_locs_uasc = merged.loc[mask, 'index_sc']
            error_locs_oc3 = merged.loc[mask, 'index']

            return {'UASC': error_locs_uasc.unique().tolist(), 'OC3': error_locs_oc3.unique().tolist()}

    return error, _validate


def validate_197B():
    error = ErrorDefinition(
        code='197B',
        description="SDQ score or reason for no SDQ should be reported for 4- or 17-year-olds.",
        affected_fields=['SDQ_REASON', 'DOB'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs or 'Episodes' not in dfs:
            return {}
        oc2 = add_CLA_column(dfs, 'OC2')

        start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
        oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
        oc2['dob_4'] = oc2['DOB'] + pd.DateOffset(years=4)
        oc2['dob_17'] = oc2['DOB'] + pd.DateOffset(years=17)

        errors = (
            (
                ((oc2['dob_4'] >= start) & (oc2['dob_4'] <= end))
                | ((oc2['dob_17'] >= start) & (oc2['dob_17'] <= end))
            )
            & oc2['CONTINUOUSLY_LOOKED_AFTER']
            & oc2['SDQ_SCORE'].isna()
            & oc2['SDQ_REASON'].isna()
        )

        return {'OC2': oc2[errors].index.to_list()}

    return error, _validate


def validate_157():
    error = ErrorDefinition(
        code='157',
        description="Child is aged 4 years or over at the beginning of the year or 16 years or under at the end of the "
                    "year and Strengths and Difficulties Questionnaire (SDQ) 1 has been recorded as the reason for no "
                    "Strengths and Difficulties Questionnaire (SDQ) score.",
        affected_fields=['SDQ_REASON', 'DOB'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs or 'Episodes' not in dfs:
            return {}
        oc2 = add_CLA_column(dfs, 'OC2')

        start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        endo = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
        oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')

        ERRRR = (
                oc2['CONTINUOUSLY_LOOKED_AFTER']
                & (oc2['DOB'] + pd.DateOffset(years=4) <= start)
                & (oc2['DOB'] + pd.DateOffset(years=16) >= endo)
                & oc2['SDQ_SCORE'].isna()
                & (oc2['SDQ_REASON'] == 'SDQ1')
        )

        return {'OC2': oc2[ERRRR].index.to_list()}

    return error, _validate


def validate_357():
    error = ErrorDefinition(
        code='357',
        description='If this is the first episode ever for this child, reason for new episode must be S.  '
                    'Check whether there is an episode immediately preceding this one, which has been left out.  '
                    'If not the reason for new episode code must be amended to S.',
        affected_fields=['RNE'],
    )

    # !# Potential false negatives for first episodes before the current collection year?
    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        eps = dfs['Episodes']
        collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        eps['DECOM'] = pd.to_datetime(eps['DECOM'], format='%d/%m/%Y', errors='coerce')

        eps = eps.loc[eps['DECOM'].notnull()]

        first_eps = (eps
            .loc[eps.groupby('CHILD')['DECOM'].idxmin()]
            .loc[eps['DECOM'] >= collection_start])

        errs = first_eps[first_eps['RNE'] != 'S'].index.to_list()

        return {'Episodes': errs}

    return error, _validate


def validate_117():
    error = ErrorDefinition(
        code='117',
        description='Date of decision that a child should/should no longer be placed for adoption is beyond the current collection year or after the child ceased to be looked after.',
        affected_fields=['DATE_PLACED_CEASED', 'DATE_PLACED', 'DEC', 'REC', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placed_adoption = dfs['PlacedAdoption']
            collection_end = dfs['metadata']['collection_end']

            # datetime
            placed_adoption['DATE_PLACED_CEASED'] = pd.to_datetime(placed_adoption['DATE_PLACED_CEASED'],
                                                                   format='%d/%m/%Y', errors='coerce')
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # Drop nans and continuing episodes
            episodes = episodes.dropna(subset=['DECOM'])
            episodes = episodes[episodes['REC'] != 'X1']

            episodes = episodes.loc[episodes.groupby('CHILD')['DECOM'].idxmax()]

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            p4a_cols = ['DATE_PLACED', 'DATE_PLACED_CEASED']

            # latest episodes
            merged = episodes.merge(placed_adoption, on='CHILD', how='left', suffixes=['_eps', '_pa'])
            mask = (
                    (merged['DATE_PLACED'] > collection_end)
                    | (merged['DATE_PLACED'] > merged['DEC'])
                    | (merged['DATE_PLACED_CEASED'] > collection_end)
                    | (merged['DATE_PLACED_CEASED'] > merged['DEC'])
            )
            # If provided <DATE_PLACED> and/or <DATE_PLACED_CEASED> must not be > <COLLECTION_END_DATE> or <DEC> of latest episode where <REC> not = 'X1'
            pa_error_locs = merged.loc[mask, 'index_pa']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locs.tolist(), 'PlacedAdoption': pa_error_locs.unique().tolist()}

    return error, _validate


def validate_118():
    error = ErrorDefinition(
        code='118',
        description='Date of decision that a child should no longer be placed for adoption is before the current collection year or before the date the child started to be looked after.',
        affected_fields=['DECOM', 'DECOM', 'LS']
    )

    def _validate(dfs):
        if ('PlacedAdoption' not in dfs) or ('Episodes' not in dfs):
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            episodes = dfs['Episodes']
            collection_start = dfs['metadata']['collection_start']
            code_list = ['V3', 'V4']

            # datetime
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            placed_adoption['DATE_PLACED_CEASED'] = pd.to_datetime(placed_adoption['DATE_PLACED_CEASED'],
                                                                   format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')

            # <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
            filter_by_ls = episodes[~(episodes['LS'].isin(code_list))]
            earliest_episode_idxs = filter_by_ls.groupby('CHILD')['DECOM'].idxmin()
            earliest_episodes = episodes[episodes.index.isin(earliest_episode_idxs)]

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            earliest_episodes.reset_index(inplace=True)

            # merge
            merged = earliest_episodes.merge(placed_adoption, on='CHILD', how='left', suffixes=['_eps', '_pa'])

            # drop rows where DATE_PLACED_CEASED is not provided
            merged = merged.dropna(subset=['DATE_PLACED_CEASED'])
            # If provided <DATE_PLACED_CEASED> must not be prior to <COLLECTION_START_DATE> or <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
            mask = (merged['DATE_PLACED_CEASED'] < merged['DECOM']) | (merged['DATE_PLACED_CEASED'] < collection_start)
            # error locations
            pa_error_locs = merged.loc[mask, 'index_pa']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locs.tolist(), 'PlacedAdoption': pa_error_locs.unique().tolist()}

    return error, _validate


# !# potential false negatives, as this only operates on current and previous year data
def validate_199():
    error = ErrorDefinition(
        code='199',
        description='Episode information shows child has been previously adopted from care. '
                    '[NOTE: This only tests the current and previous year data loaded into the tool]',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['current_year_index'] = episodes.index

            if 'Episodes_last' in dfs:
                episodes_last = dfs['Episodes_last']
                episodes = pd.concat([episodes, episodes_last], axis=0)

        episodes['is_ad'] = episodes['REC'].isin(['E11', 'E12']).astype(int)
        episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

        episodes = (episodes
                    .dropna(subset=['DECOM'])
                    .sort_values('DECOM'))

        episodes['ads_to_d8'] = episodes.groupby('CHILD')['is_ad'].cumsum()
        error_mask = (
                (episodes['ads_to_d8'] > 0)  # error if there have been any adoption episodes to date...
                & ~((episodes['ads_to_d8']) == 1 & episodes['REC'].isin(['E11', 'E12']))  # ...unless this is the first
        )

        error_locations = (episodes
                           .loc[error_mask, 'current_year_index']
                           .dropna()
                           .sort_values()
                           .astype(int)
                           .to_list())

        return {'Episodes': error_locations}

    return error, _validate

def validate_352():
    error = ErrorDefinition(
        code='352',
        description='Child who started to be looked after was aged 18 or over.',
        affected_fields=['DECOM', 'RNE'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            header['DOB18'] = header['DOB'] + pd.DateOffset(years=18)

            episodes_merged = episodes.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                           indicator=True).set_index('index')

            care_start = episodes_merged['RNE'].str.upper().astype(str).isin(['S'])
            started_over_18 = episodes_merged['DOB18'] <= episodes_merged['DECOM']

            error_mask = care_start & started_over_18

            error_locations = episodes_merged.index[error_mask].unique()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_209():
    error = ErrorDefinition(
        code='209',
        description='Child looked after is of school age and should not have an unknown Unique Pupil Number (UPN) code of UN1.',
        affected_fields=['UPN', 'DOB']
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            collection_start = dfs['metadata']['collection_start']
            # convert to datetime
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            yr = collection_start.year - 1
            reference_date = pd.to_datetime('31/08/' + str(yr), format='%d/%m/%Y', errors='coerce')
            # If <DOB> >= 4 years prior to 31/08/YYYY then <UPN> should not be 'UN1' Note: YYYY in this instance refers to the year prior to the collection start (for collection year 2019-2020, it would be looking at the 31/08/2018).
            mask = (reference_date >= (header['DOB'] + pd.offsets.DateOffset(years=4))) & (header['UPN'] == 'UN1')
            # error locations
            error_locs_header = header.index[mask]
            return {'Header': error_locs_header.tolist()}

    return error, _validate


def validate_198():
    error = ErrorDefinition(
        code='198',
        description="Child has not been looked after continuously for at least 12 months at 31 March but a reason "
                    "for no Strengths and Difficulties (SDQ) score has been completed. ",
        affected_fields=['SDQ_REASON'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC2' not in dfs:
            return {}

        oc2 = add_CLA_column(dfs, 'OC2')

        error_mask = oc2['SDQ_REASON'].notna() & ~oc2['CONTINUOUSLY_LOOKED_AFTER']

        error_locs = oc2.index[error_mask].to_list()

        return {'OC2': error_locs}

    return error, _validate


def validate_185():
    error = ErrorDefinition(
        code='185',
        description="Child has not been looked after continuously for at least 12 months at " +
                    "31 March but a Strengths and Difficulties (SDQ) score has been completed.",
        affected_fields=['SDQ_SCORE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC2' not in dfs:
            return {}

        oc2 = add_CLA_column(dfs, 'OC2')

        error_mask = oc2['SDQ_SCORE'].notna() & ~oc2['CONTINUOUSLY_LOOKED_AFTER']

        error_locs = oc2.index[error_mask].to_list()

        return {'OC2': error_locs}

    return error, _validate


def validate_186():
    error = ErrorDefinition(
        code='186',
        description="Children aged 4 or over at the start of the year and children aged under 17 at the " +
                    "end of the year and who have been looked after for at least 12 months continuously " +
                    "should have a Strengths and Difficulties (SDQ) score completed.",
        affected_fields=['SDQ_SCORE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC2' not in dfs:
            return {}

        oc2 = dfs['OC2']

        collection_start_str = dfs['metadata']['collection_start']
        collection_end_str = dfs['metadata']['collection_end']

        collection_start = pd.to_datetime(collection_start_str, format='%d/%m/%Y', errors='coerce')
        collection_end = pd.to_datetime(collection_end_str, format='%d/%m/%Y', errors='coerce')
        oc2['DOB_dt'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')

        oc2 = add_CLA_column(dfs, 'OC2')

        oc2['4th_bday'] = oc2['DOB_dt'] + pd.DateOffset(years=4)
        oc2['17th_bday'] = oc2['DOB_dt'] + pd.DateOffset(years=17)
        error_mask = (
                (oc2['4th_bday'] <= collection_start)
                & (oc2['17th_bday'] > collection_end)
                & oc2['CONTINUOUSLY_LOOKED_AFTER']
                & oc2[['SDQ_SCORE', 'SDQ_REASON']].isna().any(axis=1)
        )

        oc2_errors = oc2.loc[error_mask].index.to_list()

        return {'OC2': oc2_errors}

    return error, _validate


def validate_187():
    error = ErrorDefinition(
        code='187',
        description="Child cannot be looked after continuously for 12 months at " +
                    "31 March (OC2) and have any of adoption or care leavers returns completed.",
        affected_fields=['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR',  # OC3
                         'IN_TOUCH', 'ACTIV', 'ACCOM'],  # AD1
    )

    def _validate(dfs):
        if (
                'OC3' not in dfs
                or 'AD1' not in dfs
                or 'Episodes' not in dfs
        ):
            return {}

        # add 'CONTINUOUSLY_LOOKED_AFTER' column
        ad1, oc3 = add_CLA_column(dfs, ['AD1', 'OC3'])

        # OC3
        should_be_blank = ['IN_TOUCH', 'ACTIV', 'ACCOM']
        oc3_mask = oc3['CONTINUOUSLY_LOOKED_AFTER'] & oc3[should_be_blank].notna().any(axis=1)
        oc3_error_locs = oc3[oc3_mask].index.to_list()

        # AD1
        should_be_blank = ['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']
        ad1_mask = ad1['CONTINUOUSLY_LOOKED_AFTER'] & ad1[should_be_blank].notna().any(axis=1)
        ad1_error_locs = ad1[ad1_mask].index.to_list()

        return {'AD1': ad1_error_locs,
                'OC3': oc3_error_locs}

    return error, _validate


def validate_188():
    error = ErrorDefinition(
        code='188',
        description="Child is aged under 4 years at the end of the year, "
                    "but a Strengths and Difficulties (SDQ) score or a reason "
                    "for no SDQ score has been completed. ",
        affected_fields=['SDQ_SCORE', 'SDQ_REASON'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}

        oc2 = dfs['OC2']

        collection_end_str = dfs['metadata']['collection_end']

        collection_end = pd.to_datetime(collection_end_str, format='%d/%m/%Y', errors='coerce')
        oc2['DOB_dt'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')

        oc2['4th_bday'] = oc2['DOB_dt'] + pd.DateOffset(years=4)
        error_mask = (
                (oc2['4th_bday'] > collection_end)
                & oc2[['SDQ_SCORE', 'SDQ_REASON']].notna().any(axis=1)
        )

        oc2_errors = oc2.loc[error_mask].index.to_list()

        return {'OC2': oc2_errors}

    return error, _validate


def validate_190():
    error = ErrorDefinition(
        code='190',
        description="Child has not been looked after continuously for at least 12 months at 31 March but one or more "
                    "data items relating to children looked after for 12 months have been completed.",
        affected_fields=['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                         'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']
        ,  # AD1
    )

    def _validate(dfs):
        if (
                'OC2' not in dfs
                or 'Episodes' not in dfs
        ):
            return {}

        # add 'CONTINUOUSLY_LOOKED_AFTER' column
        oc2 = add_CLA_column(dfs, 'OC2')

        should_be_blank = ['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                           'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']

        mask = ~oc2['CONTINUOUSLY_LOOKED_AFTER'] & oc2[should_be_blank].notna().any(axis=1)
        error_locs = oc2[mask].index.to_list()

        return {'OC2': error_locs}

    return error, _validate


def validate_191():
    error = ErrorDefinition(
        code='191',
        description="Child has been looked after continuously for at least 12 months at 31 March but one or more "
                    "data items relating to children looked after for 12 months have been left blank.",
        affected_fields=['IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE', 'CHILD'],  # OC2 and Episodes
    )

    def _validate(dfs):
        if (
                'OC2' not in dfs
                or 'Episodes' not in dfs
        ):
            return {}

        
          
        # add 'CONTINUOUSLY_LOOKED_AFTER' column
        oc2 = add_CLA_column(dfs, 'OC2')
        eps = add_CLA_column(dfs, 'Episodes')

        # CHILD is in OC2 but missing data
        should_be_present = ['IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE']
        mask_oc2 = oc2['CONTINUOUSLY_LOOKED_AFTER'] & oc2[should_be_present].isna().any(axis=1)
        oc2_error_locs = oc2[mask_oc2].index.to_list()

        # CHILD is not in OC2 at all
        eps['DECOM'] = pd.to_datetime(eps['DECOM'], format='%d/%m/%Y', errors='coerce')  
        eps = eps.reset_index()
        eps = eps.loc[eps.groupby('CHILD')['DECOM'].idxmin()]
        merged_eps = eps.merge(oc2[['CHILD']], on='CHILD', how='left', indicator=True)
        mask_eps = merged_eps['CONTINUOUSLY_LOOKED_AFTER'] & (merged_eps['_merge'] == 'left_only')
        eps_error_locs = merged_eps.loc[mask_eps, 'index'].to_list()
      
      
        return {'OC2': oc2_error_locs, 'Episodes': eps_error_locs}

    return error, _validate


def validate_607():
    error = ErrorDefinition(
        code='607',
        description='Child ceased to be looked after in the year, but mother field has not been completed.',
        affected_fields=['DEC', 'REC', 'MOTHER', 'LS', 'SEX']
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']
            collection_start = dfs['metadata']['collection_start']
            collection_end = dfs['metadata']['collection_end']
            code_list = ['V3', 'V4']

            # convert to datetiime format
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)

            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])

            # CEASED_TO_BE_LOOKED_AFTER = DEC is not null and REC is filled but not equal to X1
            CEASED_TO_BE_LOOKED_AFTER = merged['DEC'].notna() & ((merged['REC'] != 'X1') & merged['REC'].notna())
            # and <LS> not = ‘V3’ or ‘V4’
            check_LS = ~(merged['LS'].isin(code_list))
            # and <DEC> is in <CURRENT_COLLECTION_YEAR
            check_DEC = (collection_start <= merged['DEC']) & (merged['DEC'] <= collection_end)
            # Where <CEASED_TO_BE_LOOKED_AFTER> = ‘Y’, and <LS> not = ‘V3’ or ‘V4’ and <DEC> is in <CURRENT_COLLECTION_YEAR> and <SEX> = ‘2’ then <MOTHER> should be provided.
            mask = CEASED_TO_BE_LOOKED_AFTER & check_LS & check_DEC & (merged['SEX'] == '2') & (merged['MOTHER'].isna())
            header_error_locs = merged.loc[mask, 'index_er']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Episodes': eps_error_locs.tolist(), 'Header': header_error_locs.unique().tolist()}

    return error, _validate


def validate_210():
    error = ErrorDefinition(
        code='210',
        description='Children looked after for more than a week at 31 March should not have an unknown Unique Pupil Number (UPN) code of UN4.',
        affected_fields=['UPN', 'DECOM']
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']
            collection_end = dfs['metadata']['collection_end']
            # convert to datetime
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            yr = collection_end.year
            reference_date = ref_date = pd.to_datetime('24/03/' + str(yr), format='%d/%m/%Y', errors='coerce')
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            # the logical way is to merge left on UPN but that will be a one to many merge and may not go as well as a many to one merge that we've been doing.
            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])
            # If <UPN> = 'UN4' then no episode <DECOM> must be >` = 24/03/YYYY Note: YYYY refers to the current collection year.
            mask = (merged['UPN'] == 'UN4') & (merged['DECOM'] >= reference_date)
            # error locations
            error_locs_header = merged.loc[mask, 'index_er']
            error_locs_eps = merged.loc[mask, 'index_eps']
            return {'Episodes': error_locs_eps.tolist(), 'Header': error_locs_header.unique().tolist()}

    return error, _validate


def validate_625():
    error = ErrorDefinition(
        code='625',
        description='Date of birth of the first child is beyond the end of this reporting year or the date the child ceased to be looked after.',
        affected_fields=['MC_DOB', 'DEC']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']
            collection_end = dfs['metadata']['collection_end']

            # datetime conversion
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            header['MC_DOB'] = pd.to_datetime(header['MC_DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            # prepare to merge
            header.reset_index(inplace=True)
            episodes.reset_index(inplace=True)
            # latest episodes
            eps_last_indices = episodes.groupby('CHILD')['DEC'].idxmax()
            latest_episodes = episodes[episodes.index.isin(eps_last_indices)]
            merged = latest_episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])
            # If provided <MC_DOB> must not be > <COLLECTION_END> or <DEC> of latest episode
            mask = (merged['MC_DOB'] > collection_end) | (merged['MC_DOB'] > merged['DEC'])
            header_error_locs = merged.loc[mask, 'index_er']
            eps_error_locs = merged.loc[mask, 'index_eps']
            return {'Header': header_error_locs.unique().tolist(), 'Episodes': eps_error_locs.tolist()}

    return error, _validate


# !# big potential false positives, as this only operates on the current and previous year data
# should use collection start/end & DOB to exclude children whose first/last episode dates mean we probably can't tell
def validate_1001():
    error = ErrorDefinition(
        code='1001',
        description='The episodes recorded for this young person suggest they are not a relevant or a former relevant '
                    'child and therefore should not have care leaver information completed. '
                    '[NOTE: This tool can only test the current and previous year data loaded into the tool - this '
                    'check may generate false positives if a child had episodes prior to last year\'s collection.]',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        # requiring 'Episodes_last' to reduce false positive rate, though more could be done
        if any(table_name not in dfs for table_name in ('Episodes', 'OC3', 'Header', 'Episodes_last')):
            return {}
        elif any(len(dfs[table_name]) == 0 for table_name in ('Episodes', 'OC3', 'Header', 'Episodes_last')):
            return {}
        else:
            current_eps = dfs['Episodes']
            prev_eps = dfs['Episodes_last']
            oc3 = dfs['OC3']
            header = dfs['Header']

            collection_end = dfs['metadata']['collection_end']
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')

            episodes = pd.concat([current_eps, prev_eps], axis=0)
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            episodes.drop_duplicates(subset=['CHILD', 'DECOM'])

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            header = header[header['DOB'].notnull()]
            header['DOB14'] = header['DOB'] + pd.DateOffset(years=14)
            header['DOB16'] = header['DOB'] + pd.DateOffset(years=16)

            # Drop children who are over 20 years old at collection end,
            # as we would not expect to see sufficient episodes in the past 2 years of data
            header = header[header['DOB'] + pd.DateOffset(years=20) > collection_end]

            # this should drop any episodes duplicated between years.
            # keep='first' should drop prev. year's missing DEC
            episodes = episodes.sort_values('DEC').drop_duplicates(['CHILD', 'DECOM'], keep='first')

            # fill in missing final DECs with the collection year's end date
            missing_last_DECs = (
                    episodes.index.isin(episodes.groupby('CHILD')['DECOM'].idxmax())
                    & episodes['DEC'].isna()
            )
            episodes.loc[missing_last_DECs, 'DEC'] = collection_end

            # Work out how long child has been in care since 14th and 16th birthdays.
            episodes_merged = (episodes
                               .reset_index()
                               .merge(header[['CHILD', 'DOB', 'DOB14', 'DOB16']],
                                      how='inner', on=['CHILD'], suffixes=('', '_header'), indicator=True)
                               .set_index('index'))

            # Drop all episodes with V3/V4 legal status
            v3v4_ls = episodes_merged['LS'].str.upper().isin(['V3', 'V4'])
            index_v3v4_ls = episodes_merged.loc[v3v4_ls].index
            episodes_merged.drop(index_v3v4_ls, inplace=True)

            if len(episodes_merged) == 0:
                return {'OC3': []}

            episodes_merged['DECOM14'] = episodes_merged[["DECOM", "DOB14"]].max(axis=1)
            episodes_merged['DECOM16'] = episodes_merged[["DECOM", "DOB16"]].max(axis=1)

            episodes_merged['DURATION14'] = (episodes_merged['DEC'] - episodes_merged['DECOM14']).dt.days.clip(lower=0)
            episodes_merged['DURATION16'] = (episodes_merged['DEC'] - episodes_merged['DECOM16']).dt.days.clip(lower=0)

            episodes_merged['TOTAL14'] = episodes_merged.groupby('CHILD')['DURATION14'].transform('sum')
            episodes_merged['TOTAL16'] = episodes_merged.groupby('CHILD')['DURATION16'].transform('sum')

            totals = episodes_merged[['CHILD', 'TOTAL14', 'TOTAL16']].drop_duplicates('CHILD')

            oc3 = oc3.merge(totals, how='left')

            # print(episodes_merged[['CHILD', 'DOB', 'DURATION14', 'TOTAL14', 'DURATION16', 'TOTAL16']])
            # print(episodes_merged[['CHILD', 'DOB', 'LS', 'REC', 'EVER_ADOPTED', 'DURATION V3/V4']])

            has_care_after_14 = oc3['TOTAL14'] >= 91
            has_care_after_16 = oc3['TOTAL16'] >= 1

            valid_care_leaver = has_care_after_14 & has_care_after_16

            # Find out if child has been adopted
            episodes_max = episodes.groupby('CHILD')['DECOM'].idxmax()
            episodes_max = episodes.loc[episodes_max]
            episodes_adopted = episodes_max[episodes_max['REC'].str.upper().isin(['E11', 'E12'])]
            adopted = oc3['CHILD'].isin(episodes_adopted['CHILD'])

            error_mask = adopted | ~valid_care_leaver

            validation_error_locations = oc3.index[error_mask]

            return {'OC3': validation_error_locations.tolist()}

    return error, _validate


def validate_1010():
    error = ErrorDefinition(
        code='1010',
        description='This child has no episodes loaded for current year even though there was an open episode of '
                    + 'care at the end of the previous year, and care leaver data has been entered.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs or 'OC3' not in dfs:
            return {}

        else:
            episodes = dfs['Episodes']
            episodes_last = dfs['Episodes_last']
            oc3 = dfs['OC3']

            # convert DECOM to datetime, drop missing/invalid sort by CHILD then DECOM,
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last = episodes_last.dropna(subset=['DECOM']).sort_values(['CHILD', 'DECOM'], ascending=True)

            # Keep only the final episode for each child (ie where the following row has a different CHILD value)
            episodes_last = episodes_last[
                episodes_last['CHILD'].shift(-1) != episodes_last['CHILD']
                ]
            # Keep only the final episodes that were still open
            episodes_last = episodes_last[episodes_last['DEC'].isna()]

            # The remaining children ought to have episode data in the current year if they are in OC3
            has_current_episodes = oc3['CHILD'].isin(episodes['CHILD'])
            has_open_episode_last = oc3['CHILD'].isin(episodes_last['CHILD'])

            error_mask = ~has_current_episodes & has_open_episode_last

            validation_error_locations = oc3.index[error_mask]

            return {'OC3': validation_error_locations.tolist()}

    return error, _validate


def validate_525():
    error = ErrorDefinition(
        code='525',
        description='A child for whom the decision to be placed for adoption has been reversed cannot be adopted during the year.',
        affected_fields=['DATE_PLACED_CEASED', 'DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR',
                         'LS_ADOPTR']
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            ad1 = dfs['AD1']
            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            ad1.reset_index(inplace=True)

            merged = placed_adoption.merge(ad1, on='CHILD', how='left', suffixes=['_placed', '_ad1'])
            # If <DATE_PLACED_CEASED> not Null, then <DATE_INT>; <DATE_MATCH>; <FOSTER_CARE>; <NB_ADOPTR>; <SEX_ADOPTR>; and <LS_ADOPTR> should not be provided
            mask = merged['DATE_PLACED_CEASED'].notna() & (
                    merged['DATE_INT'].notna() | merged['DATE_MATCH'].notna() | merged['FOSTER_CARE'].notna() |
                    merged['NB_ADOPTR'].notna() | merged['SEX_ADOPTR'].notna() | merged['LS_ADOPTR'].notna())
            # error locations
            pa_error_locs = merged.loc[mask, 'index_placed']
            ad_error_locs = merged.loc[mask, 'index_ad1']
            # return result
            return {'PlacedAdoption': pa_error_locs.tolist(), 'AD1': ad_error_locs.tolist()}

    return error, _validate


def validate_335():
    error = ErrorDefinition(
        code='335',
        description='The current foster value (0) suggests that child is not adopted by current foster carer, but last placement is A2, A3, or A5. Or the current foster value (1) suggests that child is adopted by current foster carer, but last placement is A1, A4 or A6.',
        affected_fields=['PLACE', 'FOSTER_CARE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            ad1 = dfs['AD1']

            # prepare to merge
            episodes.reset_index(inplace=True)
            ad1.reset_index(inplace=True)
            merged = episodes.merge(ad1, on='CHILD', how='left', suffixes=['_eps', '_ad1'])

            # Where <PL> = 'A2', 'A3' or 'A5' and <DEC> = 'E1', 'E11', 'E12' <FOSTER_CARE> should not be '0'; Where <PL> = ‘A1’, ‘A4’ or ‘A6’ and <REC> = ‘E1’, ‘E11’, ‘E12’ <FOSTER_CARE> should not be ‘1’.
            mask = (
                    merged['REC'].isin(['E1', 'E11', 'E12']) & (
                    (merged['PLACE'].isin(['A2', 'A3', 'A5']) & (merged['FOSTER_CARE'].astype(str) == '0'))
                    | (merged['PLACE'].isin(['A1', 'A4', 'A6']) & (merged['FOSTER_CARE'].astype(str) == '1'))
            )
            )
            eps_error_locs = merged.loc[mask, 'index_eps']
            ad1_error_locs = merged.loc[mask, 'index_ad1']

            # use .unique since join is many to one
            return {'Episodes': eps_error_locs.tolist(), 'AD1': ad1_error_locs.unique().tolist()}

    return error, _validate


def validate_215():
    error = ErrorDefinition(
        code='215',
        description='Child has care leaver information but one or more data items relating to children looked after for 12 months have been completed.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM', 'CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK',
                         'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'OC2' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            oc2 = dfs['OC2']
            # prepare to merge
            oc3.reset_index(inplace=True)
            oc2.reset_index(inplace=True)
            merged = oc3.merge(oc2, on='CHILD', how='left', suffixes=['_3', '_2'])
            # If any of <IN_TOUCH>, <ACTIV> or <ACCOM> have been provided then <CONVICTED>; <HEALTH_CHECK>; <IMMUNISATIONS>; <TEETH_CHECK>; <HEALTH_ASSESSMENT>; <SUBSTANCE MISUSE>; <INTERVENTION_RECEIVED>; <INTERVENTION_OFFERED>; should not be provided
            mask = (merged['IN_TOUCH'].notna() | merged['ACTIV'].notna() | merged['ACCOM'].notna()) & (
                    merged['CONVICTED'].notna() | merged['HEALTH_CHECK'].notna() | merged['IMMUNISATIONS'].notna() |
                    merged['TEETH_CHECK'].notna() | merged['HEALTH_ASSESSMENT'].notna() | merged[
                        'SUBSTANCE_MISUSE'].notna() | merged['INTERVENTION_RECEIVED'].notna() | merged[
                        'INTERVENTION_OFFERED'].notna())

            # error locations
            oc3_error_locs = merged.loc[mask, 'index_3']
            oc2_error_locs = merged.loc[mask, 'index_2']
            return {'OC3': oc3_error_locs.tolist(), 'OC2': oc2_error_locs.tolist()}

    return error, _validate


def validate_399():
    error = ErrorDefinition(
        code='399',
        description='Mother field, review field or participation field are completed but '
                    + 'child is looked after under legal status V3 or V4.',
        affected_fields=['MOTHER', 'LS', 'REVIEW', 'REVIEW_CODE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs or 'Reviews' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']
            reviews = dfs['Reviews']

            code_list = ['V3', 'V4']
            # Rule adjustment: if child has any other episodes where LS is not V3 or V4, rule should not be triggered. Trigger error 399 only if all child episodes

            # Column that will contain True if LS of the episode is either V3 or V4
            episodes['LS_CHECKS'] = episodes['LS'].isin(code_list)

            # Column that will contain True only if all LSs, for a child, are either V3 or V4
            episodes['LS_CHECK'] = episodes.groupby('CHILD')['LS_CHECKS'].transform('min')

            eps = episodes.loc[episodes['LS_CHECK'] == True].copy()

            # prepare to merge
            eps['index_eps'] = eps.index
            header['index_hdr'] = header.index
            reviews['index_revs'] = reviews.index

            # merge
            merged = (eps.merge(header, on='CHILD', how='left')
                      .merge(reviews, on='CHILD', how='left'))

            # If <LS> = 'V3' or 'V4' then <MOTHER>, <REVIEW> and <REVIEW_CODE> should not be provided
            mask = merged['LS_CHECK'] & (
                    merged['MOTHER'].notna() | merged['REVIEW'].notna() | merged['REVIEW_CODE'].notna())

            # Error locations
            eps_errors = merged.loc[mask, 'index_eps'].dropna().unique()
            header_errors = merged.loc[mask, 'index_hdr'].dropna().unique()
            revs_errors = merged.loc[mask, 'index_revs'].dropna().unique()

            return {'Episodes': eps_errors.tolist(),
                    'Header': header_errors.tolist(),
                    'Reviews': revs_errors.tolist()}

    return error, _validate


def validate_189():
    error = ErrorDefinition(
        code='189',
        description='Child is aged 17 years or over at the beginning of the year, but an Strengths and Difficulties '
                    + '(SDQ) score or a reason for no Strengths and Difficulties (SDQ) score has been completed.',
        affected_fields=['DOB', 'SDQ_SCORE', 'SDQ_REASON']
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            collection_start = dfs['metadata']['collection_start']

            # datetime format allows appropriate comparison between dates
            oc2['DOB'] = pd.to_datetime(oc2['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')

            # If <DOB> >17 years prior to <COLLECTION_START_DATE> then <SDQ_SCORE> and <SDQ_REASON> should not be provided
            mask = ((oc2['DOB'] + pd.offsets.DateOffset(years=17)) <= collection_start) & (
                    oc2['SDQ_REASON'].notna() | oc2['SDQ_SCORE'].notna())
            # That is, raise error if collection_start > DOB + 17years
            oc_error_locs = oc2.index[mask]
            return {'OC2': oc_error_locs.tolist()}

    return error, _validate


def validate_226():
    error = ErrorDefinition(
        code='226',
        description='Reason for placement change is not required.',
        affected_fields=['REASON_PLACE_CHANGE', 'PLACE']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']

            code_list = ['T0', 'T1', 'T2', 'T3', 'T4']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            # create column to see previous REASON_PLACE_CHANGE
            episodes = episodes.sort_values(['CHILD', 'DECOM'])
            episodes['PREVIOUS_REASON'] = episodes.groupby('CHILD')['REASON_PLACE_CHANGE'].shift(1)
            # If <PL> = 'T0'; 'T1'; 'T2'; 'T3' or 'T4' then <REASON_PLACE_CHANGE> should be null in current episode and current episode - 1
            mask = episodes['PLACE'].isin(code_list) & (
                    episodes['REASON_PLACE_CHANGE'].notna() | episodes['PREVIOUS_REASON'].notna())

            # error locations
            error_locs = episodes.index[mask]
        return {'Episodes': error_locs.tolist()}

    return error, _validate


def validate_358():
    error = ErrorDefinition(
        code='358',
        description='Child with this legal status should not be under 10.',
        affected_fields=['DECOM', 'DOB', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']
            code_list = ['J1', 'J2', 'J3']

            # convert dates to datetime format
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])

            # Where <LS> = ‘J1’ or ‘J2’ or ‘J3’ then <DOB> should <= to 10 years prior to <DECOM>
            mask = merged['LS'].isin(code_list) & (merged['DOB'] + pd.offsets.DateOffset(years=10) >= merged['DECOM'])
            # That is, raise error if DECOM <= DOB + 10years

            # error locations
            header_error_locs = merged.loc[mask, 'index_er']
            episode_error_locs = merged.loc[mask, 'index_eps']
            # one to many join implies use .unique on the 'one'
            return {'Episodes': episode_error_locs.tolist(), 'Header': header_error_locs.unique().tolist()}

    return error, _validate


def validate_407():
    error = ErrorDefinition(
        code='407',
        description='Reason episode ceased is Special Guardianship Order, but child has reached age 18.',
        affected_fields=['DEC', 'DOB', 'REC']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']
            code_list = ['E45', 'E46', 'E47', 'E48']

            # convert dates to datetime format
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            # prepare to merge
            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)
            merged = episodes.merge(header, on='CHILD', how='left', suffixes=['_eps', '_er'])

            # If <REC> = ‘E45’ or ‘E46’ or ‘E47’ or ‘E48’ then <DOB> must be < 18 years prior to <DEC>
            mask = merged['REC'].isin(code_list) & (merged['DOB'] + pd.offsets.DateOffset(years=18) < merged['DEC'])
            # That is, raise error if DEC > DOB + 10years

            # error locations
            header_error_locs = merged.loc[mask, 'index_er']
            episode_error_locs = merged.loc[mask, 'index_eps']
            # one to many join implies use .unique on the 'one'
            return {'Episodes': episode_error_locs.tolist(), 'Header': header_error_locs.unique().tolist()}

    return error, _validate


def validate_1007():
    error = ErrorDefinition(
        code='1007',
        description='Care leaver information is not required for 17- or 18-year olds who are still looked after [on '
                    'their 17th or 18th birthday.]',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'OC3' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            oc3 = dfs['OC3']
            collection_end = dfs['metadata']['collection_end']
            # convert dates to datetime format
            oc3['DOB'] = pd.to_datetime(oc3['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(collection_end, format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y')
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y')

            # prepare to merge
            episodes.reset_index(inplace=True)
            oc3.reset_index(inplace=True)
            merged = episodes.merge(oc3, on='CHILD', how='left', suffixes=['_eps', '_oc3'])
            this_year = collection_end.year

            # If <DOB> < 19 and >= to 17 years prior to <COLLECTION_END_DATE> and current episode <DEC> and or <REC>
            # not provided then <IN_TOUCH>, <ACTIV> and <ACCOM> should not be provided
            check_age = (merged['DOB'] + pd.offsets.DateOffset(years=17) <= collection_end) & (
                    merged['DOB'] + pd.offsets.DateOffset(years=19) > collection_end)
            # That is, check that 17<=age<19

            merged['bday'] = merged['DOB'].apply(lambda x: x.replace(year=this_year))

            merged.loc[merged['bday'] > collection_end, 'bday'] -= pd.DateOffset(years=1)

            in_care_on_bday = (
                (merged['DECOM'] <= merged['bday'])
                & (merged['DEC'] > merged['bday'])
            )
            print(in_care_on_bday)
            # if either DEC or REC are absent
            mask = check_age & in_care_on_bday & merged[['IN_TOUCH', 'ACTIV', 'ACCOM']].notna().any(axis=1)
            # Then raise an error if either IN_TOUCH, ACTIV, or ACCOM have been provided too

            # error locations
            oc3_error_locs = merged.loc[mask, 'index_oc3']
            episode_error_locs = merged.loc[mask, 'index_eps']
            # one to many join implies use .unique on the 'one'
            return {'OC3': oc3_error_locs.unique().tolist()}

    return error, _validate


def validate_442():
    error = ErrorDefinition(
        code='442',
        description='Unique Pupil Number (UPN) field is not completed.',
        affected_fields=['UPN']
    )

    def _validate(dfs):
        if ('Episodes' not in dfs) or ('Header' not in dfs):
            return {}
        else:
            episodes = dfs['Episodes']
            header = dfs['Header']

            episodes.reset_index(inplace=True)
            header.reset_index(inplace=True)

            code_list = ['V3', 'V4']

            # merge to get all children for which episodes have been recorded.
            merged = episodes.merge(header, on=['CHILD'], how='inner', suffixes=['_eps', '_er'])
            # Where any episode present, with an <LS> not = 'V3' or 'V4' then <UPN> must be provided
            mask = (~merged['LS'].isin(code_list)) & merged['UPN'].isna()
            header_error_locs = merged.loc[mask, 'index_er']

            return {
                    # Select unique values since many episodes are joined to one header
                    # and multiple errors will be raised for the same index.
                    'Header': header_error_locs.dropna().unique().tolist()}

    return error, _validate


def validate_344():
    error = ErrorDefinition(
        code='344',
        description='The record shows the young person has died or returned home to live with parent(s) or someone with parental responsibility for a continuous period of 6 months or more, but activity and/or accommodation on leaving care have been completed.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM']
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            # If <IN_TOUCH> = 'DIED' or 'RHOM' then <ACTIV> and <ACCOM> should not be provided (0 for this)
            mask = ((oc3['IN_TOUCH'] == 'DIED') | (oc3['IN_TOUCH'] == 'RHOM')) & (
                    (oc3['ACTIV'].astype(str) != '0') | (oc3['ACCOM'].astype(str) != '0'))
            error_locations = oc3.index[mask]
            return {'OC3': error_locations.to_list()}

    return error, _validate


def validate_345():
    error = ErrorDefinition(
        code='345',
        description='The data collection record shows the local authority is in touch with this young person, but activity and/or accommodation data items are zero.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM']
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            # If <IN_TOUCH> = 'Yes' then <ACTIV> and <ACCOM> must not be 0
            mask = (oc3['IN_TOUCH'] == 'YES') & ((oc3['ACTIV'].astype(str) == '0') | (oc3['ACCOM'].astype(str) == '0'))
            error_locations = oc3.index[mask]
            return {'OC3': error_locations.to_list()}

    return error, _validate


def validate_384():
    error = ErrorDefinition(
        code='384',
        description='A child receiving respite care cannot be in a long-term foster placement ',
        affected_fields=['PLACE', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            # Where <LS> = 'V3' or 'V4' then <PL> must not be 'U1' or 'U4'
            mask = ((episodes['LS'] == 'V3') | (episodes['LS'] == 'V4')) & (
                    (episodes['PLACE'] == 'U1') | (episodes['PLACE'] == 'U4'))
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_390():
    error = ErrorDefinition(
        code='390',
        description='Reason episode ceased is adopted but child has not been previously placed for adoption.',
        affected_fields=['PLACE', 'REC']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            # If <REC> = 'E11' or 'E12' then <PL> must be one of 'A3', 'A4', 'A5' or 'A6'
            mask = ((episodes['REC'] == 'E11') | (episodes['REC'] == 'E12')) & ~(
                    (episodes['PLACE'] == 'A3') | (episodes['PLACE'] == 'A4') | (episodes['PLACE'] == 'A5') | (
                    episodes['PLACE'] == 'A6'))
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_378():
    error = ErrorDefinition(
        code='378',
        description='A child who is placed with parent(s) cannot be looked after under a single period of accommodation under Section 20 of the Children Act 1989.',
        affected_fields=['PLACE', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            # the & sign supercedes the ==, so brackets are necessary here
            mask = (episodes['PLACE'] == 'P1') & (episodes['LS'] == 'V2')
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_398():
    error = ErrorDefinition(
        code='398',
        description='Distance field completed but child looked after under legal status V3 or V4.',
        affected_fields=['LS', 'HOME_POST', 'PL_POST']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = ((episodes['LS'] == 'V3') | (episodes['LS'] == 'V4')) & (
                    episodes['HOME_POST'].notna() | episodes['PL_POST'].notna())
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_451():
    error = ErrorDefinition(
        code='451',
        description='Child is still freed for adoption, but freeing orders could not be applied for since 30 December 2005.',
        affected_fields=['DEC', 'REC', 'LS']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = episodes['DEC'].isna() & episodes['REC'].isna() & (episodes['LS'] == 'D1')
            error_locations = episodes.index[mask]
            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_519():
    error = ErrorDefinition(
        code='519',
        description='Data entered on the legal status of adopters shows civil partnership couple, but data entered on genders of adopters does not show it as a couple.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR']
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            mask = (ad1['LS_ADOPTR'] == 'L2') & (
                    (ad1['SEX_ADOPTR'] != 'MM') & (ad1['SEX_ADOPTR'] != 'FF') & (ad1['SEX_ADOPTR'] != 'MF'))
            error_locations = ad1.index[mask]
            return {'AD1': error_locations.to_list()}

    return error, _validate


def validate_520():
    error = ErrorDefinition(
        code='520',
        description='Data entry on the legal status of adopters shows different gender married couple but data entry on genders of adopters shows it as a same gender couple.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR']
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}
        else:
            ad1 = dfs['AD1']
            # check condition
            mask = (ad1['LS_ADOPTR'] == 'L11') & (ad1['SEX_ADOPTR'] != 'MF')
            error_locations = ad1.index[mask]
            return {'AD1': error_locations.to_list()}

    return error, _validate


def validate_522():
    error = ErrorDefinition(
        code='522',
        description='Date of decision that the child should be placed for adoption must be on or before the date that a child should no longer be placed for adoption.',
        affected_fields=['DATE_PLACED', 'DATE_PLACED_CEASED']
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            # Convert to datetimes
            placed_adoption['DATE_PLACED_CEASED'] = pd.to_datetime(placed_adoption['DATE_PLACED_CEASED'],
                                                                   format='%d/%m/%Y', errors='coerce')
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            # Boolean mask
            mask = placed_adoption['DATE_PLACED_CEASED'] < placed_adoption['DATE_PLACED']

            error_locations = placed_adoption.index[mask]
            return {'PlacedAdoption': error_locations.to_list()}

    return error, _validate


def validate_563():
    error = ErrorDefinition(
        code='563',
        description='The child should no longer be placed for adoption but the date of the decision that the child should be placed for adoption is blank',
        affected_fields=['DATE_PLACED', 'REASON_PLACED_CEASED', 'DATE_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            placed_adoption = dfs['PlacedAdoption']
            mask = placed_adoption['REASON_PLACED_CEASED'].notna() & placed_adoption['DATE_PLACED_CEASED'].notna() & \
                   placed_adoption['DATE_PLACED'].isna()
            error_locations = placed_adoption.index[mask]
            return {'PlacedAdoption': error_locations.to_list()}

    return error, _validate


def validate_544():
    error = ErrorDefinition(
        code='544',
        description="Any child who has conviction information completed must also have immunisation, teeth check, health assessment and substance misuse problem identified fields completed.",
        affected_fields=['CONVICTED', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            convict = oc2['CONVICTED'].astype(str) == '1'
            immunisations = oc2['IMMUNISATIONS'].isna()
            teeth_ck = oc2['TEETH_CHECK'].isna()
            health_ass = oc2['HEALTH_ASSESSMENT'].isna()
            sub_misuse = oc2['SUBSTANCE_MISUSE'].isna()

            error_mask = convict & (immunisations | teeth_ck | health_ass | sub_misuse)
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}

    return error, _validate


def validate_634():
    error = ErrorDefinition(
        code='634',
        description='There are entries for previous permanence options, but child has not started to be looked after from 1 April 2016 onwards.',
        affected_fields=['LA_PERM', 'PREV_PERM', 'DATE_PERM', 'DECOM']
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PrevPerm' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            prevperm = dfs['PrevPerm']
            collection_start = dfs['metadata']['collection_start']
            # convert date field to appropriate format
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            # the maximum date has the highest possibility of satisfying the condition
            episodes['LAST_DECOM'] = episodes.groupby('CHILD')['DECOM'].transform('max')

            # prepare to merge
            episodes.reset_index(inplace=True)
            prevperm.reset_index(inplace=True)
            merged = prevperm.merge(episodes, on='CHILD', how='left', suffixes=['_prev', '_eps'])
            # If <PREV_PERM> or <LA_PERM> or <DATE_PERM> provided, then at least 1 episode must have a <DECOM> later than 01/04/2016
            mask = (merged['PREV_PERM'].notna() | merged['DATE_PERM'].notna() | merged['LA_PERM'].notna()) & (
                    merged['LAST_DECOM'] < collection_start)
            eps_error_locs = merged.loc[mask, 'index_eps']
            prevperm_error_locs = merged.loc[mask, 'index_prev']

            # return {'PrevPerm':prevperm_error_locs}
            return {'Episodes': eps_error_locs.unique().tolist(), 'PrevPerm': prevperm_error_locs.unique().tolist()}

    return error, _validate


def validate_158():
    error = ErrorDefinition(
        code='158',
        description='If a child has been recorded as receiving an intervention for their substance misuse problem, then the additional item on whether an intervention was offered should be left blank.',
        affected_fields=['INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}

        else:
            oc2 = dfs['OC2']

            error_mask = oc2['INTERVENTION_RECEIVED'].astype(str).eq('1') & oc2['INTERVENTION_OFFERED'].notna()

            error_locations = oc2.index[error_mask]

            return {'OC2': error_locations.tolist()}

    return error, _validate


def validate_133():
    error = ErrorDefinition(
        code='133',
        description='Data entry for accommodation after leaving care is invalid. If reporting on a childs accommodation after leaving care the data entry must be valid',
        affected_fields=['ACCOM'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs:
            return {}

        else:
            oc3 = dfs['OC3']
            valid_codes = ['B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2', 'G1', 'G2', 'H1', 'H2', 'K1', 'K2', 'R1',
                           'R2', 'S2', 'T1', 'T2', 'U1', 'U2', 'V1', 'V2', 'W1', 'W2', 'X2', 'Y1', 'Y2', 'Z1', 'Z2',
                           '0']

            error_mask = ~oc3['ACCOM'].isin(valid_codes)

            error_locations = oc3.index[error_mask]

            return {'OC3': error_locations.tolist()}

    return error, _validate


def validate_565():
    error = ErrorDefinition(
        code='565',
        description='The date that the child started to be missing or away from placement without authorisation has been completed but whether the child was missing or away from placement without authorisation has not been completed.',
        affected_fields=['MISSING', 'MIS_START']
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']
            mask = missing['MIS_START'].notna() & missing['MISSING'].isna()
            error_locations = missing.index[mask]
            return {'Missing': error_locations.to_list()}

    return error, _validate


def validate_433():
    error = ErrorDefinition(
        code='433',
        description='The reason for new episode suggests that this is a continuation episode, but the episode does not start on the same day as the last episode finished.',
        affected_fields=['RNE', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM_dt'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC_dt'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            episodes['original_index'] = episodes.index
            episodes.sort_values(['CHILD', 'DECOM_dt', 'DEC_dt'], inplace=True)
            episodes[['PREVIOUS_DEC', 'PREVIOUS_CHILD']] = episodes[['DEC', 'CHILD']].shift(1)

            rne_is_ongoing = episodes['RNE'].str.upper().astype(str).isin(['P', 'L', 'T', 'U', 'B'])
            date_mismatch = episodes['PREVIOUS_DEC'] != episodes['DECOM']
            missing_date = episodes['PREVIOUS_DEC'].isna() | episodes['DECOM'].isna()
            same_child = episodes['PREVIOUS_CHILD'] == episodes['CHILD']

            error_mask = rne_is_ongoing & (date_mismatch | missing_date) & same_child

            error_locations = episodes['original_index'].loc[error_mask].sort_values()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_437():
    error = ErrorDefinition(
        code='437',
        description='Reason episode ceased is child has died or is aged 18 or over but there are further episodes.',
        affected_fields=['REC'],
    )

    # !# potential false negatives, as this only operates on the current year's data
    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')

            episodes.sort_values(['CHILD', 'DECOM'], inplace=True)
            episodes[['NEXT_DECOM', 'NEXT_CHILD']] = episodes[['DECOM', 'CHILD']].shift(-1)

            # drop rows with missing DECOM as invalid/missing values can lead to errors
            episodes = episodes.dropna(subset=['DECOM'])

            ceased_e2_e15 = episodes['REC'].str.upper().astype(str).isin(['E2', 'E15'])
            has_later_episode = episodes['CHILD'] == episodes['NEXT_CHILD']

            error_mask = ceased_e2_e15 & has_later_episode

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_547():
    error = ErrorDefinition(
        code='547',
        description="Any child who has health promotion information completed must also have immunisation, teeth check, health assessment and substance misuse problem identified fields completed.",
        affected_fields=['HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            healthck = oc2['HEALTH_CHECK'].astype(str) == '1'
            immunisations = oc2['IMMUNISATIONS'].isna()
            teeth_ck = oc2['TEETH_CHECK'].isna()
            health_ass = oc2['HEALTH_ASSESSMENT'].isna()
            sub_misuse = oc2['SUBSTANCE_MISUSE'].isna()

            error_mask = healthck & (immunisations | teeth_ck | health_ass | sub_misuse)
            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}

    return error, _validate


def validate_635():
    error = ErrorDefinition(
        code='635',
        description='There are entries for date of order and local authority code where previous permanence option was arranged but previous permanence code is Z1',
        affected_fields=['LA_PERM', 'DATE_PERM', 'PREV_PERM']
    )

    def _validate(dfs):
        if 'PrevPerm' not in dfs:
            return {}
        else:
            prev_perm = dfs['PrevPerm']
            # raise and error if either LA_PERM or DATE_PERM are present, yet PREV_PERM is absent.
            mask = ((prev_perm['LA_PERM'].notna() | prev_perm['DATE_PERM'].notna()) & prev_perm['PREV_PERM'].isna())

            error_locations = prev_perm.index[mask]
        return {'PrevPerm': error_locations.to_list()}

    return error, _validate


def validate_550():
    error = ErrorDefinition(
        code='550',
        description='A placement provider code of PR0 can only be associated with placement P1.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']

            mask = (episodes['PLACE'] != 'P1') & episodes['PLACE_PROVIDER'].eq('PR0')

            validation_error_locations = episodes.index[mask]
            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_217():
    error = ErrorDefinition(
        code='217',
        description='Children who are placed for adoption with current foster carers (placement types A3 or A5) must have a reason for new episode of S, T or U.',
        affected_fields=['PLACE', 'DECOM', 'RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            max_decom_allowed = pd.to_datetime('01/04/2015', format='%d/%m/%Y', errors='coerce')
            reason_new_ep = ['S', 'T', 'U']
            place_codes = ['A3', 'A5']

            mask = (episodes['PLACE'].isin(place_codes) & (episodes['DECOM'] >= max_decom_allowed)) & ~episodes[
                'RNE'].isin(reason_new_ep)

            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_205A():
    error = ErrorDefinition(
        code = '205A',
        description = 'Child identified as UASC last year is no longer UASC this year, but date UASC ceased in both '
                      'years does not support this.',
        affected_fields=['CHILD', 'UASC'],
    )

    def _validate(dfs):
        try:
            file_format = dfs['metadata']['file_format']
        except KeyError as e:
            raise MissingMetadataError(*e.args)

        if 'UASC' not in dfs or 'UASC_last' not in dfs:
            return {}
        elif file_format == 'xml' and ('Header' not in dfs or 'Header_last' not in dfs):
            return {}
        elif all(i in dfs for i in ('Header', 'Header_last', 'UASC', 'UASC_last')):
            return_header_errors = True

            uasc = dfs['UASC']
            uasc_last = dfs['UASC_last']
            header = dfs['Header']
            header_last = dfs['Header_last']
        elif file_format == 'csv':
            # for csv uploads, the Header table gets the UASC column added in ingress if UASC is present,
            # as does Header_last if UASC_last is present.  Therefore use Header['UASC'] if present, else make our own
            uasc = dfs['UASC']
            uasc_last = dfs['UASC_last']
            if 'Header' in dfs:
                return_header_errors = True

                header = dfs['Header']
            else:
                return_header_errors = False

                header = uasc[['CHILD']].copy()
                header['UASC'] = '0'
                uasc_inds = uasc.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
                header.loc[uasc_inds, 'UASC'] = '1'
            if 'Header_last' in dfs:
                header_last = dfs['Header_last']
            else:
                header_last = uasc_last[['CHILD']].copy()
                header_last['UASC'] = '0'
                uasc_inds = uasc_last.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
                header_last.loc[uasc_inds, 'UASC'] = '1'
        else:
            raise RuntimeError("Table selection failed (205C). This shouldn't be possible.")
        if 'UASC' not in header.columns or 'UASC' not in header_last.columns:
            return {}

        collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
        collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
        collection_start_last = collection_start + pd.offsets.DateOffset(years=-1)
        collection_end_last = collection_end + pd.offsets.DateOffset(years=-1)

        uasc_last['DUC'] = pd.to_datetime(uasc_last['DUC'],format='%d/%m/%Y',errors='coerce')

        header.reset_index(inplace=True)
        uasc.reset_index(inplace=True)

        merged_current = (uasc[['CHILD', 'DUC', 'index']]
                          .merge(header[['CHILD', 'UASC', 'index']], how='left',
                                 on='CHILD', suffixes=('_uasc','_header')))

        merged_last = (uasc_last[['CHILD', 'DUC']]
                       .merge(header_last[['CHILD', 'UASC']], how='left',
                                   on='CHILD'))

        all_merged = (merged_current
                      .merge(merged_last, how='left',
                              on=['CHILD'], suffixes=('', '_last'), indicator=True))

        last_year_only = (
                (all_merged['UASC'].astype(str) != '1')
                & (all_merged['UASC_last'].astype(str) == '1')
        )
        duc_last_in_prev_year = (
                (all_merged['DUC_last'] >= collection_start_last)
                & (all_merged['DUC_last'] <= collection_end_last)
        )
        uasc_current_duc = all_merged['DUC'].notna()

        error_mask = last_year_only & (uasc_current_duc | ~duc_last_in_prev_year)

        error_locations_uasc = (all_merged
                                .loc[error_mask, 'index_uasc']
                                .dropna()
                                .astype(int)
                                .sort_values())
        error_locations_header = (all_merged.loc[error_mask, 'index_header']
                                  .dropna()
                                  .astype(int)
                                  .sort_values())
        if return_header_errors:
            return {'UASC': error_locations_uasc.to_list(),
                    'Header': error_locations_header.to_list()}
        else:
            return {'UASC': error_locations_uasc.to_list()}

    return error, _validate

def validate_205B():
    error = ErrorDefinition(
        code = '205B',
        description = 'Child previously identified as UASC is also UASC this year, but date UASC ceased in both years does not support this.',
        affected_fields=['DUC', 'UASC'],
    )

    def _validate(dfs):
        try:
            file_format = dfs['metadata']['file_format']
        except KeyError as e:
            raise MissingMetadataError(*e.args)

        if 'UASC' not in dfs or 'UASC_last' not in dfs:
            return {}
        elif file_format == 'xml' and ('Header' not in dfs or 'Header_last' not in dfs):
            return {}
        elif all(i in dfs for i in ('Header', 'Header_last', 'UASC', 'UASC_last')):
            return_header_errors = True

            uasc = dfs['UASC']
            uasc_last = dfs['UASC_last']
            header = dfs['Header']
            header_last = dfs['Header_last']
        elif file_format == 'csv':
            # for csv uploads, the Header table gets the UASC column added in ingress if UASC is present,
            # as does Header_last if UASC_last is present.  Therefore use Header['UASC'] if present, else make our own
            uasc = dfs['UASC']
            uasc_last = dfs['UASC_last']
            if 'Header' in dfs:
                return_header_errors = True

                header = dfs['Header']
            else:
                return_header_errors = False

                header = uasc[['CHILD']].copy()
                header['UASC'] = '0'
                uasc_inds = uasc.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
                header.loc[uasc_inds , 'UASC'] = '1'
            if 'Header_last' in dfs:
                header_last = dfs['Header_last']
            else:
                header_last = uasc_last[['CHILD']].copy()
                header_last['UASC'] = '0'
                uasc_inds = uasc_last.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
                header_last.loc[uasc_inds, 'UASC'] = '1'
        else:
            raise RuntimeError("Table selection failed (205B). This shouldn't be possible.")
        if 'UASC' not in header.columns or 'UASC' not in header_last.columns:
            return {}
        collection_start = pd.to_datetime(dfs['metadata']['collection_start'],format='%d/%m/%Y',errors='coerce')
        collection_end = pd.to_datetime(dfs['metadata']['collection_end'],format='%d/%m/%Y',errors='coerce')
        collection_start_last = collection_start + pd.offsets.DateOffset(years=-1)
        collection_end_last = collection_end + pd.offsets.DateOffset(years=-1)

        uasc['DOB'] = pd.to_datetime(uasc['DOB'], format='%d/%m/%Y', errors='coerce')
        uasc['DUC'] = pd.to_datetime(uasc['DUC'], format='%d/%m/%Y', errors='coerce')
        uasc_last['DOB'] = pd.to_datetime(uasc_last['DOB'], format='%d/%m/%Y', errors='coerce')
        uasc_last['DUC'] = pd.to_datetime(uasc_last['DUC'], format='%d/%m/%Y', errors='coerce')
        uasc['DOB18'] = uasc_last['DOB'] + pd.offsets.DateOffset(years=18)

        header['HDR_INDEX'] = header.index
        header_last.reset_index(inplace=True)

        header.reset_index(inplace=True)
        uasc.reset_index(inplace=True)

        merged_current = (uasc[['CHILD', 'DUC', 'DOB18', 'index']]
                          .merge(header[['CHILD', 'UASC', 'index']], how='left',
                                 on='CHILD', suffixes=('_uasc','_header')))

        merged_last = (uasc_last[['CHILD', 'DUC']]
                       .merge(header_last[['CHILD', 'UASC']], how='left',
                                   on='CHILD'))

        all_merged = (merged_current
                      .merge(merged_last, how='left',
                              on=['CHILD'], suffixes=('', '_last'), indicator=True))

        uasc_in_both_years = ((all_merged['UASC'].astype(str) == '1')
                              & (all_merged['UASC_last'].astype(str) == '1'))
        uasc_current_duc = (all_merged['DUC'] >= collection_start) & (all_merged['DUC'] <= collection_end)
        prev_duc_is_18th = all_merged['DUC_last'] == all_merged['DOB18']
        current_duc_is_18th = all_merged['DUC'] == all_merged['DUC_last']

        print(pd.concat((all_merged, pd.DataFrame({'b': uasc_in_both_years,
                                                   'cd':uasc_current_duc,
                                                   'c18': current_duc_is_18th,
                                                   'p18': prev_duc_is_18th})), axis=1).to_string())

        error_mask = uasc_in_both_years & ((~uasc_current_duc & ~current_duc_is_18th) | ~prev_duc_is_18th)

        error_locations_uasc = all_merged.loc[error_mask, 'index_uasc']
        error_locations_header = all_merged.loc[error_mask, 'index_header']

        if return_header_errors:
            return {'UASC': error_locations_uasc.to_list(),
                    'Header': error_locations_header.to_list()}
        else:
            return {'UASC': error_locations_uasc.to_list()}

    return error, _validate

def validate_205C():
    error = ErrorDefinition(
        code = '205C',
        description = 'Child not identified as UASC either this year or last year but date UASC ceased has been provided.',
        affected_fields=['DUC','UASC'],
    )

    def _validate(dfs):
        try:
            file_format = dfs['metadata']['file_format']
        except KeyError as e:
            raise MissingMetadataError(*e.args)

        if 'UASC' not in dfs or 'UASC_last' not in dfs:
            return {}
        elif file_format == 'xml' and ('Header' not in dfs or 'Header_last' not in dfs):
            return {}
        elif all(i in dfs for i in ('Header', 'Header_last', 'UASC', 'UASC_last')):
            return_header_errors = True

            uasc = dfs['UASC']
            uasc_last = dfs['UASC_last']
            header = dfs['Header']
            header_last = dfs['Header_last']
        elif file_format == 'csv':
            # for csv uploads, the Header table gets the UASC column added in ingress if UASC is present,
            # as does Header_last if UASC_last is present.  Therefore use Header['UASC'] if present, else make our own
            uasc = dfs['UASC']
            uasc_last = dfs['UASC_last']
            if 'Header' in dfs:
                return_header_errors = True

                header = dfs['Header']
            else:
                return_header_errors = False

                header = uasc[['CHILD']].copy()
                header['UASC'] = '0'
                uasc_inds = uasc.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
                header.loc[uasc_inds , 'UASC'] = '1'
            if 'Header_last' in dfs:
                header_last = dfs['Header_last']
            else:
                header_last = uasc_last[['CHILD']].copy()
                header_last['UASC'] = '0'
                uasc_inds = uasc_last.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
                header_last.loc[uasc_inds, 'UASC'] = '1'
        else:
            raise RuntimeError("Table selection failed (205C). This shouldn't be possible.")
        if 'UASC' not in header.columns or 'UASC' not in header_last.columns:
            return {}

        collection_start = pd.to_datetime(dfs['metadata']['collection_start'],format='%d/%m/%Y',errors='coerce')
        collection_end = pd.to_datetime(dfs['metadata']['collection_end'],format='%d/%m/%Y',errors='coerce')
        collection_start_last = collection_start + pd.offsets.DateOffset(years=-1)
        collection_end_last = collection_end + pd.offsets.DateOffset(years=-1)

        uasc['DOB'] = pd.to_datetime(uasc['DOB'], format='%d/%m/%Y', errors='coerce')
        uasc['DUC'] = pd.to_datetime(uasc['DUC'], format='%d/%m/%Y', errors='coerce')
        uasc_last['DOB'] = pd.to_datetime(uasc_last['DOB'], format='%d/%m/%Y', errors='coerce')
        uasc_last['DUC'] = pd.to_datetime(uasc_last['DUC'], format='%d/%m/%Y', errors='coerce')
        uasc['DOB18'] = uasc_last['DOB'] + pd.offsets.DateOffset(years=18)

        header['HDR_INDEX'] = header.index
        header_last.reset_index(inplace=True)

        header.reset_index(inplace=True)
        uasc.reset_index(inplace=True)

        merged_current = (uasc[['CHILD', 'DUC', 'DOB18', 'index']]
                          .merge(header[['CHILD', 'UASC', 'index']], how='left',
                                 on='CHILD', suffixes=('_uasc','_header')))

        merged_last = (uasc_last[['CHILD', 'DUC']]
                       .merge(header_last[['CHILD', 'UASC']], how='left',
                                   on='CHILD'))

        all_merged = (merged_current
                      .merge(merged_last, how='left',
                              on=['CHILD'], suffixes=('', '_last'), indicator=True))

        never_uasc = ((all_merged[['UASC', 'UASC_last']] == '0')
                      | all_merged[['UASC', 'UASC_last']].isna()).all(axis=1)
        has_duc = all_merged[['DUC', 'DUC_last']].notna().any(axis=1)

        error_mask = never_uasc & has_duc

        error_locations_uasc = (all_merged.loc[error_mask, 'index_uasc']
                                .dropna()
                                .astype(int)
                                .sort_values())
        error_locations_header = (all_merged.loc[error_mask, 'index_header']
                                             .dropna()
                                             .astype(int)
                                             .sort_values())
        print(pd.concat((all_merged, pd.DataFrame({'u':never_uasc, 'd':has_duc})), axis=1).to_string())
        if return_header_errors:
            return {'UASC': error_locations_uasc.to_list(),
                    'Header': error_locations_header.to_list()}
        else:
            return {'UASC': error_locations_uasc.to_list()}

    return error, _validate


def validate_205D():
    error = ErrorDefinition(
        code = '205D',
        description = 'Child identified as UASC this year but not identified as UASC status provided for the child last year.',
        affected_fields=['UASC', 'CHILD'],
    )

    def _validate(dfs):
        if 'Header' in dfs:
            return_header_errors = True

            header = dfs['Header']
        elif 'UASC' in dfs:
            uasc = dfs['UASC']
            return_header_errors = False

            header = uasc[['CHILD']].copy()
            header['UASC'] = '0'
            uasc_inds = uasc.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
            header.loc[uasc_inds , 'UASC'] = '1'
        else:
            return {}
        if 'Header_last' in dfs:
            header_last = dfs['Header_last']
        elif 'UASC_last' in dfs:
            uasc_last = dfs['UASC_last']
            header_last = uasc_last[['CHILD']].copy()
            header_last['UASC'] = '0'
            uasc_inds = uasc_last.drop(['CHILD', 'DOB'], axis='columns').notna().any(axis=1)
            header_last.loc[uasc_inds, 'UASC'] = '1'
        else:
            return {}
        if 'UASC' not in header.columns or 'UASC' not in header_last.columns:
            return {}
        print(header.to_string())
        print(header_last.to_string())
        all_merged = (header
                      .reset_index()
                      .merge(header_last, how='inner',
                             on=['CHILD'], suffixes=('', '_last'), indicator=True))

        error_mask = (all_merged['UASC'] == '1') & (all_merged['UASC_last'] != '1')
        print(all_merged.to_string())
        errors = all_merged.loc[error_mask, 'index'].to_list()
        if return_header_errors:
            return {'Header': errors}
        else:
            return {'UASC': errors}
    return error, _validate

def validate_518():
    error = ErrorDefinition(
        code='518',
        description='If reporting legal status of adopters is L4 then the genders of adopters should be coded as MM or FF. MM = the adopting couple are both males. FF = the adopting couple are both females.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            error_mask = AD1['LS_ADOPTR'].eq('L4') & ~AD1['SEX_ADOPTR'].isin(['MM', 'FF'])

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}

    return error, _validate


def validate_517():
    error = ErrorDefinition(
        code='517',
        description='If reporting legal status of adopters is L3 then the genders of adopters should be coded as MF. MF = the adopting couple are male and female.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            error_mask = AD1['LS_ADOPTR'].eq('L3') & ~AD1['SEX_ADOPTR'].isin(['MF'])

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}

    return error, _validate


def validate_558():
    error = ErrorDefinition(
        code='558',
        description='If a child has been adopted, then the decision to place them for adoption has not been disrupted and the date of the decision that a child should no longer be placed for adoption should be left blank. if the REC code is either E11 or E12 then the DATE PLACED CEASED date should not be provided',
        affected_fields=['DATE_PLACED_CEASED', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placedAdoptions = dfs['PlacedAdoption']

            episodes = episodes.reset_index()

            rec_codes = ['E11', 'E12']

            placeEpisodes = episodes[episodes['REC'].isin(rec_codes)]

            merged = placeEpisodes.merge(placedAdoptions, how='left', on='CHILD').set_index('index')

            episodes_with_errors = merged[merged['DATE_PLACED_CEASED'].notna()]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_453():
    error = ErrorDefinition(
        code='453',
        description='Contradiction between placement distance in the last episode of the previous year and in the first episode of the current year.',
        affected_fields=['PL_DISTANCE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        if 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes_last = dfs['Episodes_last']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['PL_DISTANCE'] = pd.to_numeric(episodes['PL_DISTANCE'], errors='coerce')
            episodes_last['PL_DISTANCE'] = pd.to_numeric(episodes_last['PL_DISTANCE'], errors='coerce')

            # drop rows with missing DECOM before finding idxmin/max, as invalid/missing values can lead to errors
            episodes = episodes.dropna(subset=['DECOM'])
            episodes_last = episodes_last.dropna(subset=['DECOM'])

            episodes_min = episodes.groupby('CHILD')['DECOM'].idxmin()
            episodes_last_max = episodes_last.groupby('CHILD')['DECOM'].idxmax()

            episodes = episodes[episodes.index.isin(episodes_min)]
            episodes_last = episodes_last[episodes_last.index.isin(episodes_last_max)]

            episodes_merged = episodes.reset_index().merge(episodes_last, how='left', on=['CHILD'],
                                                           suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = episodes_merged['_merge'] == 'both'
            same_rne = episodes_merged['RNE'] == episodes_merged['RNE_last']
            last_year_open = episodes_merged['DEC_last'].isna()
            different_pl_dist = abs(episodes_merged['PL_DISTANCE'] - episodes_merged['PL_DISTANCE_last']) >= 0.2

            error_mask = in_both_years & same_rne & last_year_open & different_pl_dist

            validation_error_locations = episodes.index[error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_516():
    error = ErrorDefinition(
        code='516',
        description='The episode data submitted for this child does not show that he/she was with their former foster carer(s) during the year.If the code in the reason episode ceased is E45 or E46 the child must have a placement code of U1 to U6.',
        affected_fields=['REC', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        else:
            episodes = dfs['Episodes']
            place_codes = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6']
            rec_codes = ['E45', 'E46']

            error_mask = episodes['REC'].isin(rec_codes) & ~episodes['PLACE'].isin(place_codes)

            validation_error_locations = episodes.index[error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_511():
    error = ErrorDefinition(
        code='511',
        description='If reporting that the number of person(s) adopting the looked after child is two adopters then the code should only be MM, FF or MF. MM = the adopting couple are both males; FF = the adopting couple are both females; MF = The adopting couple are male and female.',
        affected_fields=['NB_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            mask = AD1['NB_ADOPTR'].astype(str).eq('2') & AD1['SEX_ADOPTR'].isin(['M1', 'F1'])

            validation_error_mask = mask
            validation_error_locations = AD1.index[validation_error_mask]

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_524():
    error = ErrorDefinition(
        code='524',
        description='If reporting legal status of adopters is L12 then the genders of adopters should be coded as MM or FF. MM = the adopting couple are both males. FF = the adopting couple are both females',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):
        if 'AD1' not in dfs:
            return {}

        else:
            AD1 = dfs['AD1']

            error_mask = AD1['LS_ADOPTR'].eq('L12') & ~AD1['SEX_ADOPTR'].isin(['MM', 'FF'])

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}

    return error, _validate


def validate_441():
    error = ErrorDefinition(
        code='441',
        description='Participation method indicates child was 4 years old or over at the time of the review, but the date of birth and review date indicates the child was under 4 years old.',
        affected_fields=['DOB', 'REVIEW', 'REVIEW_CODE'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}
        else:
            reviews = dfs['Reviews']
            reviews['DOB'] = pd.to_datetime(reviews['DOB'], format='%d/%m/%Y', errors='coerce')
            reviews['REVIEW'] = pd.to_datetime(reviews['REVIEW'], format='%d/%m/%Y', errors='coerce')
            reviews = reviews.dropna(subset=['REVIEW', 'DOB'])

            mask = reviews['REVIEW_CODE'].isin(['PN1', 'PN2', 'PN3', 'PN4', 'PN5', 'PN6', 'PN7']) & (
                    reviews['REVIEW'] < reviews['DOB'] + pd.offsets.DateOffset(years=4))

            validation_error_mask = mask

            validation_error_locations = reviews.index[validation_error_mask]

            return {'Reviews': validation_error_locations.tolist()}

    return error, _validate


def validate_184():
    error = ErrorDefinition(
        code='184',
        description='Date of decision that a child should be placed for adoption is before the child was born.',
        affected_fields=['DATE_PLACED',  # PlacedAdoptino
                         'DOB'],  # Header
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            child_record = dfs['Header']
            placed_for_adoption = dfs['PlacedAdoption']

            all_data = (placed_for_adoption
                        .reset_index()
                        .merge(child_record, how='left', on='CHILD', suffixes=[None, '_P4A']))

            all_data['DATE_PLACED'] = pd.to_datetime(all_data['DATE_PLACED'], format='%d/%m/%Y', errors='coerce')
            all_data['DOB'] = pd.to_datetime(all_data['DOB'], format='%d/%m/%Y', errors='coerce')

            mask = (all_data['DATE_PLACED'] >= all_data['DOB']) | all_data['DATE_PLACED'].isna()

            validation_error = ~mask

            validation_error_locations = all_data[validation_error]['index'].unique()

            return {'PlacedAdoption': validation_error_locations.tolist()}

    return error, _validate


def validate_612():
    error = ErrorDefinition(
        code='612',
        description="Date of birth field has been completed but mother field indicates child is not a mother.",
        affected_fields=['SEX', 'MOTHER', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            error_mask = (
                    ((header['MOTHER'].astype(str) == '0') | header['MOTHER'].isna())
                    & (header['SEX'].astype(str) == '2')
                    & header['MC_DOB'].notna()
            )

            validation_error_locations = header.index[error_mask]

            return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_552():
    """
  This error checks that the first adoption episode is after the last decision !
  If there are multiple of either there may be unexpected results !
  """

    error = ErrorDefinition(
        code="552",
        description="Date of Decision to place a child for adoption should be on or prior to the date that the child was placed for adoption.",
        # Field that defines date of decision to place a child for adoption is DATE_PLACED and the start of adoption is defined by DECOM with 'A' placement types.
        affected_fields=['DATE_PLACED', 'DECOM'],
    )

    def _validate(dfs):
        if ('PlacedAdoption' not in dfs) or ('Episodes' not in dfs):
            return {}
        else:
            # get the required datasets
            placed_adoption = dfs['PlacedAdoption']
            episodes = dfs['Episodes']
            # keep index values so that they stay the same when needed later on for error locations
            placed_adoption.reset_index(inplace=True)
            episodes.reset_index(inplace=True)

            adoption_eps = episodes[episodes['PLACE'].isin(['A3', 'A4', 'A5', 'A6'])].copy()
            # find most recent adoption decision
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')
            # remove rows where either of the required values have not been filled.
            placed_adoption = placed_adoption[placed_adoption['DATE_PLACED'].notna()]

            placed_adoption_inds = placed_adoption.groupby('CHILD')['DATE_PLACED'].idxmax(skipna=True)
            last_decision = placed_adoption.loc[placed_adoption_inds]

            # first time child started adoption
            adoption_eps["DECOM"] = pd.to_datetime(adoption_eps['DECOM'], format='%d/%m/%Y', errors='coerce')
            adoption_eps = adoption_eps[adoption_eps['DECOM'].notna()]

            adoption_eps_inds = adoption_eps.groupby('CHILD')['DECOM'].idxmin(skipna=True)
            # full information of first adoption
            first_adoption = adoption_eps.loc[adoption_eps_inds]

            # date of decision and date of start of adoption (DECOM) have to be put in one table
            merged = first_adoption.merge(last_decision, on=['CHILD'], how='left', suffixes=['_EP', '_PA'])

            # check to see if date of decision to place is less than or equal to date placed.
            decided_after_placed = merged["DECOM"] < merged["DATE_PLACED"]

            # find the corresponding location of error values per file.
            episode_error_locs = merged.loc[decided_after_placed, 'index_EP']
            placedadoption_error_locs = merged.loc[decided_after_placed, 'index_PA']

            return {"PlacedAdoption": placedadoption_error_locs.to_list(), "Episodes": episode_error_locs.to_list()}

    return error, _validate


def validate_551():
    error = ErrorDefinition(
        code='551',
        description='Child has been placed for adoption but there is no date of the decision that the child should be placed for adoption.',
        affected_fields=['DATE_PLACED', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placedAdoptions = dfs['PlacedAdoption']

            episodes = episodes.reset_index()

            place_codes = ['A3', 'A4', 'A5', 'A6']

            placeEpisodes = episodes[episodes['PLACE'].isin(place_codes)]

            merged = placeEpisodes.merge(placedAdoptions, how='left', on='CHILD').set_index('index')

            episodes_with_errors = merged[merged['DATE_PLACED'].isna()]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_557():
    error = ErrorDefinition(
        code='557',
        description="Child for whom the decision was made that they should be placed for adoption has left care " +
                    "but was not adopted and information on the decision that they should no longer be placed for " +
                    "adoption items has not been completed.",
        affected_fields=['DATE_PLACED_CEASED', 'REASON_PLACED_CEASED',  # PlacedAdoption
                         'PLACE', 'LS', 'REC'],  # Episodes
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        if 'PlacedAdoption' not in dfs:
            return {}
        else:
            eps = dfs['Episodes']
            placed = dfs['PlacedAdoption']

            eps = eps.reset_index()
            placed = placed.reset_index()

            child_placed = eps['PLACE'].isin(['A3', 'A4', 'A5', 'A6'])
            order_granted = eps['LS'].isin(['D1', 'E1'])
            not_adopted = ~eps['REC'].isin(['E11', 'E12']) & eps['REC'].notna() & (eps['REC'] != 'X1')

            placed['ceased_incomplete'] = (
                    placed['DATE_PLACED_CEASED'].isna() | placed['REASON_PLACED_CEASED'].isna()
            )

            eps = eps[(child_placed | order_granted) & not_adopted]

            eps = eps.merge(placed, on='CHILD', how='left', suffixes=['_EP', '_PA'], indicator=True)

            eps = eps[(eps['_merge'] == 'left_only') | eps['ceased_incomplete']]

            EP_errors = eps['index_EP']
            PA_errors = eps['index_PA'].dropna()

            return {
                'Episodes': EP_errors.to_list(),
                'PlacedAdoption': PA_errors.to_list(),
            }

    return error, _validate


def validate_207():
    error = ErrorDefinition(
        code='207',
        description='Mother status for the current year disagrees with the mother status already recorded for this child.',
        affected_fields=['MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']
            episodes = dfs['Episodes']

            header.reset_index(inplace=True)
          
            header_merged = header.merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True)

            header_merged = header_merged.merge(episodes[['CHILD']], on='CHILD', how='left', suffixes=('', '_eps'), indicator='_eps')

            in_both_years = header_merged['_merge'] == 'both'
            has_no_episodes = header_merged['_eps'] == 'left_only'
            mother_is_different = header_merged['MOTHER'].astype(str) != header_merged['MOTHER_last'].astype(str)
            mother_was_true = header_merged['MOTHER_last'].astype(str) == '1'

            error_mask = in_both_years & ~has_no_episodes & mother_is_different & mother_was_true

            error_locations = list(header_merged.loc[error_mask, 'index'].unique())

            return {'Header': error_locations}

    return error, _validate


def validate_523():
    error = ErrorDefinition(
        code='523',
        description="Date of decision that the child should be placed for adoption should be the same date as the decision that adoption is in the best interest (date should be placed).",
        affected_fields=['DATE_PLACED', 'DATE_INT'],
    )

    def _validate(dfs):
        if ("AD1" not in dfs) or ("PlacedAdoption" not in dfs):
            return {}
        else:
            placed_adoption = dfs["PlacedAdoption"]
            ad1 = dfs["AD1"]
            # keep initial index values to be reused for locating errors later on.
            placed_adoption.reset_index(inplace=True)
            ad1.reset_index(inplace=True)

            # convert to datetime to enable comparison
            placed_adoption['DATE_PLACED'] = pd.to_datetime(placed_adoption['DATE_PLACED'], format="%d/%m/%Y",
                                                            errors='coerce')
            ad1["DATE_INT"] = pd.to_datetime(ad1['DATE_INT'], format='%d/%m/%Y', errors='coerce')

            # drop rows where either of the required values have not been filled.
            placed_adoption = placed_adoption[placed_adoption["DATE_PLACED"].notna()]
            ad1 = ad1[ad1["DATE_INT"].notna()]

            # bring corresponding values together from both dataframes
            merged_df = placed_adoption.merge(ad1, on=['CHILD'], how='inner', suffixes=["_PA", "_AD"])
            # find error values
            different_dates = merged_df['DATE_INT'] != merged_df['DATE_PLACED']
            # map error locations to corresponding indices
            pa_error_locations = merged_df.loc[different_dates, 'index_PA']
            ad1_error_locations = merged_df.loc[different_dates, 'index_AD']

            return {"PlacedAdoption": pa_error_locations.to_list(), "AD1": ad1_error_locations.to_list()}

    return error, _validate


def validate_3001():
    error = ErrorDefinition(
        code='3001',
        description='Where care leavers information is being returned for a young person around their 17th birthday, the accommodation cannot be with their former foster carer(s).',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        if 'OC3' not in dfs:
            return {}
        else:
            header = dfs['Header']
            oc3 = dfs['OC3']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            header['DOB17'] = header['DOB'] + pd.DateOffset(years=17)

            oc3_merged = oc3.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                 indicator=True).set_index('index')

            accom_foster = oc3_merged['ACCOM'].str.upper().astype(str).isin(['Z1', 'Z2'])
            age_17_in_year = (oc3_merged['DOB17'] <= collection_end) & (oc3_merged['DOB17'] >= collection_start)

            error_mask = accom_foster & age_17_in_year

            error_locations = oc3.index[error_mask]

            return {'OC3': error_locations.to_list()}

    return error, _validate


def validate_389():
    error = ErrorDefinition(
        code='389',
        description='Reason episode ceased is that child transferred to care of adult social care services, but child is aged under 16.',
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

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB16'] = header['DOB'] + pd.DateOffset(years=16)

            episodes_merged = episodes.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                           indicator=True).set_index('index')

            ceased_asc = episodes_merged['REC'].str.upper().astype(str).isin(['E7'])
            ceased_over_16 = episodes_merged['DOB16'] <= episodes_merged['DEC']

            error_mask = ceased_asc & ~ceased_over_16

            error_locations = episodes_merged.index[error_mask].unique()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_387():
    error = ErrorDefinition(
        code='387',
        description='Reason episode ceased is child moved into independent living arrangement, but the child is aged under 14.',
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

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB14'] = header['DOB'] + pd.DateOffset(years=14)

            episodes_merged = episodes.reset_index().merge(header, how='left', on=['CHILD'], suffixes=('', '_header'),
                                                           indicator=True).set_index('index')

            ceased_indep = episodes_merged['REC'].str.upper().astype(str).isin(['E5', 'E6'])
            ceased_over_14 = episodes_merged['DOB14'] <= episodes_merged['DEC']
            dec_present = episodes_merged['DEC'].notna()

            error_mask = ceased_indep & ~ceased_over_14 & dec_present

            error_locations = episodes_merged.index[error_mask].unique()

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_452():
    error = ErrorDefinition(
        code='452',
        description='Contradiction between local authority of placement code in the last episode of the previous year and in the first episode of the current year.',
        affected_fields=['PL_LA'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        if 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes_last = dfs['Episodes_last']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')

            episodes_min = episodes.groupby('CHILD')['DECOM'].idxmin()
            episodes_last_max = episodes_last.groupby('CHILD')['DECOM'].idxmax()

            episodes = episodes[episodes.index.isin(episodes_min)]
            episodes_last = episodes_last[episodes_last.index.isin(episodes_last_max)]

            episodes_merged = episodes.reset_index().merge(episodes_last, how='left', on=['CHILD'],
                                                           suffixes=('', '_last'), indicator=True).set_index('index')

            in_both_years = episodes_merged['_merge'] == 'both'
            same_rne = episodes_merged['RNE'] == episodes_merged['RNE_last']
            last_year_open = episodes_merged['DEC_last'].isna()
            different_pl_la = episodes_merged['PL_LA'].astype(str) != episodes_merged['PL_LA_last'].astype(str)

            error_mask = in_both_years & same_rne & last_year_open & different_pl_la

            validation_error_locations = episodes.index[error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_386():
    error = ErrorDefinition(
        code='386',
        description='Reason episode ceased is adopted but child has reached age 18.',
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

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')
            header['DOB18'] = header['DOB'] + pd.DateOffset(years=18)

            episodes_merged = (
                episodes
                    .reset_index()
                    .merge(header, how='left', on=['CHILD'], suffixes=('', '_header'), indicator=True)
                    .set_index('index')
                    .dropna(subset=['DOB18', 'DEC'])
            )

            ceased_adopted = episodes_merged['REC'].str.upper().astype(str).isin(['E11', 'E12'])
            ceased_under_18 = episodes_merged['DOB18'] > episodes_merged['DEC']

            error_mask = ceased_adopted & ~ceased_under_18

            error_locations = episodes_merged.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_363():
    error = ErrorDefinition(
        code='363',
        description='Child assessment order (CAO) lasted longer than 7 days allowed in the Children Act 1989.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        episodes = dfs['Episodes']
        collection_end_str = dfs['metadata']['collection_end']

        L2_eps = episodes[episodes['LS'] == 'L3'].copy()
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
        code='364',
        description='Sections 41-46 of Police and Criminal Evidence (PACE; 1984) severely limits ' +
                    'the time a child can be detained in custody in Local Authority (LA) accommodation.',
        affected_fields=['LS', 'DECOM', 'DEC'],
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
        code='365',
        description='Any individual short- term respite placement must not exceed 17 days.',
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
        error_mask = (episodes['LS'] == 'V3') & over_17_days

        return {'Episodes': episodes.index[error_mask].to_list()}

    return error, _validate


def validate_367():
    error = ErrorDefinition(
        code='367',
        description='The maximum amount of respite care allowable is 75 days in any 12-month period.',
        affected_fields=['LS', 'DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        episodes = dfs['Episodes']
        V3_eps = episodes[episodes['LS'] == 'V3']

        V3_eps = V3_eps.dropna(subset=['DECOM'])  # missing DECOM should get fixed before looking for this error

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
        code='440',
        description='Participation method indicates child was under 4 years old at the time of the review, but date of birth and review date indicates the child was 4 years old or over.',
        affected_fields=['DOB', 'REVIEW', 'REVIEW_CODE'],
    )

    def _validate(dfs):
        if 'Reviews' not in dfs:
            return {}
        else:
            reviews = dfs['Reviews']
            reviews['DOB'] = pd.to_datetime(reviews['DOB'], format='%d/%m/%Y', errors='coerce')
            reviews['REVIEW'] = pd.to_datetime(reviews['REVIEW'], format='%d/%m/%Y', errors='coerce')

            mask = reviews['REVIEW_CODE'].eq('PN0') & (
                    reviews['REVIEW'] > reviews['DOB'] + pd.offsets.DateOffset(years=4))

            validation_error_mask = mask
            validation_error_locations = reviews.index[validation_error_mask]

            return {'Reviews': validation_error_locations.tolist()}

    return error, _validate


def validate_514():
    error = ErrorDefinition(
        code='514',
        description='Data entry on the legal status of adopters shows a single adopter but data entry for the numbers of adopters shows it as a couple.',
        affected_fields=['LS_ADOPTR', 'SEX_ADOPTR'],
    )

    def _validate(dfs):

        if 'AD1' not in dfs:
            return {}
        else:
            AD1 = dfs['AD1']
            code_list = ['M1', 'F1']
            # Check if LS Adopter is L0 and Sex Adopter is not M1 or F1.
            error_mask = (AD1['LS_ADOPTR'] == 'L0') & (~AD1['SEX_ADOPTR'].isin(code_list))

            error_locations = AD1.index[error_mask]

            return {'AD1': error_locations.tolist()}

    return error, _validate


def validate_445():
    error = ErrorDefinition(
        code='445',
        description='D1 is not a valid code for episodes starting after December 2005.',
        affected_fields=['LS', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            max_decom_allowed = pd.to_datetime('31/12/2005', format='%d/%m/%Y', errors='coerce')

            mask = episodes['LS'].eq('D1') & (episodes['DECOM'] > max_decom_allowed)
            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_446():
    error = ErrorDefinition(
        code='446',
        description='E1 is not a valid code for episodes starting before December 2005.',
        affected_fields=['LS', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            min_decom_allowed = pd.to_datetime('01/12/2005', format='%d/%m/%Y', errors='coerce')

            mask = episodes['LS'].eq('E1') & (episodes['DECOM'] < min_decom_allowed)
            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {'Episodes': validation_error_locations.tolist()}

    return error, _validate


def validate_208():
    error = ErrorDefinition(
        code='208',
        description='Unique Pupil Number (UPN) for the current year disagrees with the Unique Pupil Number (UPN) already recorded for this child.',
        affected_fields=['UPN'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            null_now = header_merged['UPN'].isna()
            null_before = header_merged['UPN_last'].isna()
            in_both_years = header_merged['_merge'] == 'both'

            header_merged['UPN'] = header_merged['UPN'].astype(str).str.upper()
            header_merged['UPN_last'] = header_merged['UPN_last'].astype(str).str.upper()
            upn_is_different = (
                    (header_merged['UPN'] != header_merged['UPN_last'])
                    & ~(null_now & null_before)
                # exclude case where unknown both years null; leave to 442 (missing UPN)
            )

            UN2_to_5 = ['UN2', 'UN3', 'UN4', 'UN5']
            UN_codes = ['UN1', ] + UN2_to_5
            valid_unknown_change = (
                    ((header_merged['UPN_last'].eq('UN1') | null_before)  # change from UN1/null...
                     & header_merged['UPN'].isin(UN2_to_5))  # ...to UN2-5
                    | (null_before & header_merged['UPN_last'].eq('UN1'))  # OR, change from null to UN1
            )
            unknown_to_known = (
                    (header_merged['UPN_last'].isin(UN_codes) | null_before)  # was either null or an UN-code
                    & ~(header_merged['UPN'].isin(UN_codes) | null_now)  # now neither null nor UN-known
            )

            error_mask = in_both_years & upn_is_different & ~valid_unknown_change & ~unknown_to_known

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_204():
    error = ErrorDefinition(
        code='204',
        description='Ethnic origin code disagrees with the ethnic origin already recorded for this child.',
        affected_fields=['ETHNIC'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            ethnic_is_different = header_merged['ETHNIC'].astype(str).str.upper() != header_merged[
                'ETHNIC_last'].astype(str).str.upper()

            error_mask = in_both_years & ethnic_is_different

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_203():
    error = ErrorDefinition(
        code='203',
        description='Date of birth disagrees with the date of birth already recorded for this child.',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            header_last['DOB'] = pd.to_datetime(header_last['DOB'], format='%d/%m/%Y', errors='coerce')

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            dob_is_different = header_merged['DOB'].astype(str) != header_merged['DOB_last'].astype(str)

            error_mask = in_both_years & dob_is_different

            error_locations = header.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_530():
    error = ErrorDefinition(
        code='530',
        description="A placement provider code of PR4 cannot be associated with placement P1.",
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
        code='571',
        description='The date that the child ceased to be missing or away from placement without authorisation is before the start or after the end of the collection year.',
        affected_fields=['MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            missing = dfs['Missing']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            missing['fMIS_END'] = pd.to_datetime(missing['MIS_END'], format='%d/%m/%Y', errors='coerce')

            end_date_before_year = missing['fMIS_END'] < collection_start
            end_date_after_year = missing['fMIS_END'] > collection_end

            error_mask = end_date_before_year | end_date_after_year

            error_locations = missing.index[error_mask]

            return {'Missing': error_locations.to_list()}

    return error, _validate


def validate_1005():
    error = ErrorDefinition(
        code='1005',
        description='The end date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.',
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
        code='1004',
        description='The start date of the missing episode or episode that the child was away from placement without authorisation is not a valid date.',
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
        code='202',
        description='The gender code conflicts with the gender already recorded for this child.',
        affected_fields=['SEX'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_last = dfs['Header_last']

            header_merged = header.reset_index().merge(header_last, how='left', on=['CHILD'], suffixes=('', '_last'),
                                                       indicator=True).set_index('index')

            in_both_years = header_merged['_merge'] == 'both'
            sex_is_different = header_merged['SEX'].astype(str) != header_merged['SEX_last'].astype(str)

            error_mask = in_both_years & sex_is_different

            error_locations = header_merged.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_621():
    error = ErrorDefinition(
        code='621',
        description="Mother’s field has been completed but date of birth shows that the mother is younger than her child.",
        affected_fields=['DOB', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']

            header['MC_DOB'] = pd.to_datetime(header['MC_DOB'], format='%d/%m/%Y', errors='coerce')
            header['DOB'] = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce')
            mask = (header['MC_DOB'] > header['DOB']) | header['MC_DOB'].isna()

            validation_error_mask = ~mask
            validation_error_locations = header.index[validation_error_mask]

            return {'Header': validation_error_locations.tolist()}

    return error, _validate


def validate_556():
    error = ErrorDefinition(
        code='556',
        description='Date of decision that the child should be placed for adoption should be on or prior to the date that the freeing order was granted.',
        affected_fields=['DATE_PLACED', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            placedAdoptions = dfs['PlacedAdoption']

            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            placedAdoptions['DATE_PLACED'] = pd.to_datetime(placedAdoptions['DATE_PLACED'], format='%d/%m/%Y',
                                                            errors='coerce')

            episodes = episodes.reset_index()

            D1Episodes = episodes[episodes['LS'] == 'D1']

            merged = D1Episodes.reset_index().merge(placedAdoptions, how='left', on='CHILD', ).set_index('index')

            episodes_with_errors = merged[merged['DATE_PLACED'] > merged['DECOM']]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_393():
    error = ErrorDefinition(
        code='393',
        description='Child is looked after but mother field is not completed.',
        affected_fields=['MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            header = dfs['Header']
            episodes = dfs['Episodes']

            header_female = header[header['SEX'].astype(str) == '2']

            applicable_episodes = episodes[~episodes['LS'].str.upper().isin(['V3', 'V4'])]

            error_mask = header_female['CHILD'].isin(applicable_episodes['CHILD']) & header_female['MOTHER'].isna()

            error_locations = header_female.index[error_mask]

            return {'Header': error_locations.to_list()}

    return error, _validate


def validate_NoE():
    error = ErrorDefinition(
        code='NoE',
        description='This child has no episodes loaded for previous year even though child started to be looked after before this current year.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes_last = dfs['Episodes_last']
            episodes_last['DECOM'] = pd.to_datetime(episodes_last['DECOM'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')

            episodes_before_year = episodes[episodes['DECOM'] < collection_start]

            episodes_merged = episodes_before_year.reset_index().merge(episodes_last, how='left', on=['CHILD'],
                                                                       indicator=True).set_index('index')

            episodes_not_matched = episodes_merged[episodes_merged['_merge'] == 'left_only']

            error_mask = episodes.index.isin(episodes_not_matched.index)

            error_locations = episodes.index[error_mask]

            return {'Episodes': error_locations.to_list()}

    return error, _validate


def validate_356():
    error = ErrorDefinition(
        code='356',
        description='The date the episode ceased is before the date the same episode started.',
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            episodes['DECOM'] = pd.to_datetime(episodes['DECOM'], format='%d/%m/%Y', errors='coerce')
            episodes['DEC'] = pd.to_datetime(episodes['DEC'], format='%d/%m/%Y', errors='coerce')

            error_mask = episodes['DEC'].notna() & (episodes['DEC'] < episodes['DECOM'])

            return {'Episodes': episodes.index[error_mask].to_list()}

    return error, _validate


def validate_611():
    error = ErrorDefinition(
        code='611',
        description="Date of birth field is blank, but child is a mother.",
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
            'F4',
            'P4',
            'F5',
            'P5',
            'G4',
            'G5',
            'G6',
            '0'
        ]
        mask = care_leavers['ACTIV'].astype(str).isin(code_list)

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
        mask = care_leavers['IN_TOUCH'].isin(code_list)

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

        mask = placed_adoptions['REASON_PLACED_CEASED'].isin(code_list) | placed_adoptions[
            'REASON_PLACED_CEASED'].isna()

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

        place_provider_needed_and_correct = episodes['PLACE_PROVIDER'].isin(code_list_placement_provider) & ~episodes[
            'PLACE'].isin(code_list_placement_with_no_provider)

        place_provider_not_provided = episodes['PLACE_PROVIDER'].isna()

        place_provider_not_needed = episodes['PLACE_PROVIDER'].isna() & episodes['PLACE'].isin(
            code_list_placement_with_no_provider)

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

        mask = review['REVIEW'].notna() & review['REVIEW_CODE'].isin(code_list) | review['REVIEW'].isna() & review[
            'REVIEW_CODE'].isna()

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
        code='141',
        description='Date episode began is not a valid date.',
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
        code='147',
        description='Date episode ceased is not a valid date.',
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
        code='171',
        description="Date of birth of mother's child is not a valid date.",
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
            episodes = dfs['Episodes']

            home_provided = episodes['HOME_POST'].notna()
            home_details = merge_postcodes(episodes, "HOME_POST")
            home_valid = home_details['pcd'].notna()

            pl_provided = episodes['PL_POST'].notna()
            pl_details = merge_postcodes(episodes, "PL_POST")
            pl_valid = pl_details['pcd'].notna()

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
            mask = df['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4']) & df['PLACE_PROVIDER'].notna()
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
            mask = df['UPN'].str.match(r'(^((?![IOS])[A-Z]){1}(\d{12}|\d{11}[A-Z]{1})$)|^(UN[1-5])$', na=False)
            mask = ~mask & df['UPN'].notnull()
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

            df['DECOM'] = df['DECOM'].fillna('01/01/1901')  # Watch for potential future issues
            df = df.sort_values(['CHILD', 'DECOM'])

            df['DECOM_NEXT_EPISODE'] = df.groupby(['CHILD'])['DECOM'].shift(-1)

            # The max DECOM for each child is also the one with no next episode
            # And we also add the skipna option
            # grouped_decom_by_child = df.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            no_next = df.DECOM_NEXT_EPISODE.isna() & df.CHILD.notna()

            # Dataframe with the maximum DECOM removed
            max_decom_removed = df[~no_next]
            # Dataframe with the maximum DECOM only
            max_decom_only = df[no_next]

            # Case 1: If reason episode ceased is coded X1 there must be a subsequent episode
            #        starting on the same day.
            case1 = max_decom_removed[(max_decom_removed['REC'] == 'X1') &
                                      (max_decom_removed['DEC'].notna()) &
                                      (max_decom_removed['DECOM_NEXT_EPISODE'].notna()) &
                                      (max_decom_removed['DEC'] != max_decom_removed['DECOM_NEXT_EPISODE'])]

            # Case 2: If an episode ends but the child continues to be looked after, a new
            #        episode should start on the same day.The reason episode ceased code of
            #        the episode which ends must be X1.
            case2 = max_decom_removed[(max_decom_removed['REC'] != 'X1') &
                                      (max_decom_removed['REC'].notna()) &
                                      (max_decom_removed['DEC'].notna()) &
                                      (max_decom_removed['DECOM_NEXT_EPISODE'].notna()) &
                                      (max_decom_removed['DEC'] == max_decom_removed['DECOM_NEXT_EPISODE'])]

            # Case 3: If a child ceases to be looked after reason episode ceased code X1 must
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
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM', 'DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR',
                         'SEX_ADOPTR', 'LS_ADOPTR'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            oc3 = dfs['OC3']
            ad1 = dfs['AD1']
            ad1['ad1_index'] = ad1.index

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
            validation_error_locations = all_data.loc[validation_error, 'ad1_index'].unique()

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_119():
    error = ErrorDefinition(
        code='119',
        description='If the decision is made that a child should no longer be placed for adoption, then the date of this decision and the reason why this decision was made must be completed.',
        affected_fields=['REASON_PLACED_CEASED', 'DATE_PLACED_CEASED'],
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


def validate_159():
    error = ErrorDefinition(
        code='159',
        description='If a child has been recorded as not receiving an intervention for their substance misuse problem, then the additional item on whether an intervention was offered should be completed as well.',
        affected_fields=['SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            mask1 = oc2['SUBSTANCE_MISUSE'].astype(str) == '1'
            mask2 = oc2['INTERVENTION_RECEIVED'].astype(str) == '0'
            mask3 = oc2['INTERVENTION_OFFERED'].isna()

            validation_error = mask1 & mask2 & mask3
            validation_error_locations = oc2.index[validation_error]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_142():
    error = ErrorDefinition(
        code='142',
        description='A new episode has started, but the previous episode has not ended.',
        affected_fields=['DEC', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            df['DECOM'] = pd.to_datetime(df['DECOM'], format='%d/%m/%Y', errors='coerce')
            df['DEC'] = pd.to_datetime(df['DEC'], format='%d/%m/%Y', errors='coerce')

            df['DECOM'] = df['DECOM'].fillna('01/01/1901')  # Watch for potential future issues

            df['DECOM'] = df['DECOM'].replace('01/01/1901', pd.NA)

            last_episodes = df.sort_values('DECOM').reset_index().groupby(['CHILD'])['index'].last()
            ended_episodes_df = df.loc[~df.index.isin(last_episodes)]

            ended_episodes_df = ended_episodes_df[(ended_episodes_df['DEC'].isna() | ended_episodes_df['REC'].isna()) &
                                                  ended_episodes_df['CHILD'].notna() & ended_episodes_df[
                                                      'DECOM'].notna()]
            mask = ended_episodes_df.index.tolist()

            return {'Episodes': mask}

    return error, _validate


def validate_148():
    error = ErrorDefinition(
        code='148',
        description='Date episode ceased and reason episode ceased must both be coded, or both left blank.',
        affected_fields=['DEC', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']

            mask = ((df['DEC'].isna()) & (df['REC'].notna())) | ((df['DEC'].notna()) & (df['REC'].isna()))

            return {'Episodes': df.index[mask].tolist()}

    return error, _validate


def validate_151():
    error = ErrorDefinition(
        code='151',
        description='All data items relating to a childs adoption must be coded or left blank.',
        affected_fields=['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTER', 'SEX_ADOPTR', 'LS_ADOPTR'],
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

            ad1_not_null = (
                    ~na_date_int & ~na_date_match & ~na_foster_care & ~na_nb_adoptr & ~na_sex_adoptr & ~na_lsadoptr)

            validation_error = (
                                       ~na_date_int | ~na_date_match | ~na_foster_care | ~na_nb_adoptr | ~na_sex_adoptr | ~na_lsadoptr) & ~ad1_not_null
            validation_error_locations = ad1.index[validation_error]

            return {'AD1': validation_error_locations.tolist()}

    return error, _validate


def validate_182():
    error = ErrorDefinition(
        code='182',
        description='Data entries on immunisations, teeth checks, health assessments and substance misuse problem identified should be completed or all OC2 fields should be left blank.',
        affected_fields=['IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT', 'SUBSTANCE_MISUSE', 'CONVICTED',
                         'HEALTH_CHECK', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
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
        affected_fields=['PL_POST', 'URN'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            df = dfs['Episodes']
            mask = df['LS'].isin(['V3', 'V4']) & ((df['PL_POST'].notna()) | (df['URN'].notna()))
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
            place_code_list = ['H5', 'P1', 'P2', 'P3', 'R1', 'R2', 'R5', 'T0', 'T1', 'T2', 'T3', 'T4', 'Z1']
            # If <URN> provided and <URN> not = ‘XXXXXXX’, and where <PL> = ‘H5’; ‘P1’ ‘P2’ ‘P3’; ‘R1’; ‘R2’; ‘R5’; ‘T0’ ‘T1’; ‘T2’; ‘T3’; ‘T4’ or Z1 then <URN> should not be provided
            mask = (df['PLACE'].isin(place_code_list)) & (df['URN'].notna()) & (df['URN'] != 'XXXXXXX')
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
            oc3_no_nulls = oc3[oc3[['IN_TOUCH', 'ACTIV', 'ACCOM']].notna().any(axis=1)]

            hea_merge_epi = hea.merge(epi, how='left', on='CHILD', indicator=True)
            hea_not_in_epi = hea_merge_epi[hea_merge_epi['_merge'] == 'left_only']

            cohort_to_check = hea_not_in_epi.merge(oc3_no_nulls, how='inner', on='CHILD')
            error_cohort = cohort_to_check[cohort_to_check['MOTHER'].notna()]

            error_list = list(set(error_cohort['index'].to_list()))
            error_list.sort()
            return {'Header': error_list}

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
        affected_fields=['DECOM', 'DEC'],
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
            df['DOB'] = pd.to_datetime(df['DOB'], format='%d/%m/%Y', errors='coerce')
            df['MIS_START'] = pd.to_datetime(df['MIS_START'], format='%d/%m/%Y', errors='coerce')

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
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')

            epi = epi.reset_index()

            # Form the episode dataframe which has an 'RNE' of 'S' in this financial year
            epi_has_rne_of_S_in_year = epi[(epi['RNE'] == 'S') & (epi['DECOM'] >= collection_start)]
            # Merge to see
            # 1) which CHILD ids are missing from the PrevPerm file
            # 2) which CHILD are in the prevPerm file, but don't have the LA_PERM/DATE_PERM field completed where they should be
            # 3) which CHILD are in the PrevPerm file, but don't have the PREV_PERM field completed.
            merged_epi_preperm = epi_has_rne_of_S_in_year.merge(pre, on='CHILD', how='left', indicator=True)

            error_not_in_preperm = merged_epi_preperm['_merge'] == 'left_only'
            error_wrong_values_in_preperm = (merged_epi_preperm['PREV_PERM'] != 'Z1') & (
                merged_epi_preperm[['LA_PERM', 'DATE_PERM']].isna().any(axis=1))
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
        affected_fields=['DECOM', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi = epi.reset_index()
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')

            epi = epi.sort_values(['CHILD', 'DECOM'])

            epi_lead = epi.shift(1)
            epi_lead = epi_lead.reset_index()

            m_epi = epi.merge(epi_lead, left_on='index', right_on='level_0', suffixes=('', '_prev'))

            error_cohort = m_epi[(m_epi['CHILD'] == m_epi['CHILD_prev']) & (m_epi['DECOM'] < m_epi['DEC_prev'])]
            error_list = error_cohort['index'].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_502():
    error = ErrorDefinition(
        code='502',
        description="Last year's record ended with an open episode. The date on which that episode started does not match the start date of the first episode on this year’s record.",
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Episodes_last' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi_last = dfs['Episodes_last']
            epi = epi.reset_index()

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi_last['DECOM'] = pd.to_datetime(epi_last['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi_last_no_dec = epi_last[epi_last['DEC'].isna()]

            epi_min_decoms_index = epi[['CHILD', 'DECOM']].groupby(['CHILD'])['DECOM'].idxmin()

            epi_min_decom_df = epi.loc[epi_min_decoms_index, :]

            merged_episodes = epi_min_decom_df.merge(epi_last_no_dec, on='CHILD', how='inner')
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
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
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
        code='166',
        description="Date of review is invalid or blank.",
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
        code='174',
        description="Mother's child date of birth is recorded but gender shows that the child is a male.",
        affected_fields=['SEX', 'MC_DOB'],
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
        code='180',
        description="Data entry for the strengths and difficulties questionnaire (SDQ) score is invalid.",
        affected_fields=['SDQ_SCORE'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']

            oc2['SDQ_SCORE_num'] = pd.to_numeric(oc2['SDQ_SCORE'], errors='coerce')

            error_mask = oc2['SDQ_SCORE'].notna() & ~oc2['SDQ_SCORE_num'].isin(range(41))

            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.to_list()}

    return error, _validate


def validate_181():
    error = ErrorDefinition(
        code='181',
        description="Data items relating to children looked after continuously for 12 months should be completed with a 0 or 1.",
        affected_fields=['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                         'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
    )

    def _validate(dfs):
        if 'OC2' not in dfs:
            return {}
        else:
            oc2 = dfs['OC2']
            code_list = ['0', '1']

            fields_of_interest = ['CONVICTED', 'HEALTH_CHECK', 'IMMUNISATIONS', 'TEETH_CHECK', 'HEALTH_ASSESSMENT',
                                  'SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED']

            error_mask = (
                    oc2[fields_of_interest].notna()
                    & ~oc2[fields_of_interest].astype(str).isin(['0', '1'])
            ).any(axis=1)

            validation_error_locations = oc2.index[error_mask]

            return {'OC2': validation_error_locations.tolist()}

    return error, _validate


def validate_192():
    error = ErrorDefinition(
        code='192',
        description="Child has been identified as having a substance misuse problem but the additional item on whether an intervention was received has been left blank.",
        affected_fields=['SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED'],
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
        code='193',
        description="Child not identified as having a substance misuse problem but at least one of the two additional items on whether an intervention were offered and received have been completed.",
        affected_fields=['SUBSTANCE_MISUSE', 'INTERVENTION_RECEIVED', 'INTERVENTION_OFFERED'],
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


def validate_197a():
    error = ErrorDefinition(
        code='197a',
        description="Reason for no Strengths and Difficulties (SDQ) score is not required if Strengths and Difficulties Questionnaire score is filled in.",
        affected_fields=['SDQ_SCORE', 'SDQ_REASON'],
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
        affected_fields=['MIS_START', 'MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'], format='%d/%m/%Y', errors='coerce')

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
            uasc['DOB'] = pd.to_datetime(uasc['DOB'], format='%d/%m/%Y', errors='coerce')
            uasc['DUC'] = pd.to_datetime(uasc['DUC'], format='%d/%m/%Y', errors='coerce')
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
            adt['DATE_MATCH'] = pd.to_datetime(adt['DATE_MATCH'], format='%d/%m/%Y', errors='coerce')
            adt['DATE_INT'] = pd.to_datetime(adt['DATE_INT'], format='%d/%m/%Y', errors='coerce')

            # If <DATE_MATCH> provided, then <DATE_INT> must also be provided and be <= <DATE_MATCH>
            mask1 = adt['DATE_MATCH'].notna() & adt['DATE_INT'].isna()
            mask2 = adt['DATE_MATCH'].notna() & adt['DATE_INT'].notna() & (adt['DATE_INT'] > adt['DATE_MATCH'])
            mask = mask1 | mask2

            return {'AD1': adt.index[mask].to_list()}

    return error, _validate


def validate_1011():
    error = ErrorDefinition(
        code='1011',
        description='This child is recorded as having his/her care transferred to another local authority for the final episode and therefore should not have the care leaver information completed.',
        affected_fields=['IN_TOUCH', 'ACTIV', 'ACCOM'],
    )

    def _validate(dfs):
        if 'OC3' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            oc3 = dfs['OC3']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            # If final <REC> = 'E3' then <IN_TOUCH>; <ACTIV> and <ACCOM> should not be provided
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            grouped_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_decom_only = epi.loc[epi.index.isin(grouped_decom_by_child), :]
            E3_is_last = max_decom_only[max_decom_only['REC'] == 'E3']

            oc3.reset_index(inplace=True)
            cohort_to_check = oc3.merge(E3_is_last, on='CHILD', how='inner')
            error_mask = cohort_to_check[['IN_TOUCH', 'ACTIV', 'ACCOM']].notna().any(axis=1)

            error_list = cohort_to_check['index'][error_mask].to_list()
            error_list = list(set(error_list))
            error_list.sort()

            return {'OC3': error_list}

    return error, _validate


def validate_574():
    error = ErrorDefinition(
        code='574',
        description='A new missing/away from placement without authorisation period cannot start when the previous missing/away from placement without authorisation period is still open. Missing/away from placement without authorisation periods should also not overlap.',
        affected_fields=['MIS_START', 'MIS_END'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:

            mis = dfs['Missing']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'], format='%d/%m/%Y', errors='coerce')

            mis['MIS_END_FILL'] = mis['MIS_END'].fillna(mis['MIS_START'])
            mis.sort_values(['CHILD', 'MIS_END_FILL', 'MIS_START'], inplace=True)

            mis.reset_index(inplace=True)
            mis.reset_index(inplace=True)  # Twice on purpose

            mis['LAG_INDEX'] = mis['level_0'].shift(-1)

            lag_mis = mis.merge(mis, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_PREV'])

            # We're only interested in cases where there is more than one row for a child.
            lag_mis = lag_mis[lag_mis['CHILD'] == lag_mis['CHILD_PREV']]

            # A previous MIS_END date is null
            mask1 = lag_mis['MIS_END_PREV'].isna()
            # MIS_START is before previous MIS_END (overlapping dates)
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
        affected_fields=['MISSING', 'MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            error_mask = mis['MISSING'].isin(['M', 'A', 'm', 'a']) & mis['MIS_START'].isna()
            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate


def validate_566():
    error = ErrorDefinition(
        code='566',
        description='The date that the child' + chr(
            39) + 's episode of being missing or away from placement without authorisation ended has been completed but whether the child was missing or away without authorisation has not been completed.',
        affected_fields=['MISSING', 'MIS_END'],
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
        affected_fields=['RNE', 'LS', 'PLACE', 'PL_POST', 'URN', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:

            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)
            epi.fillna(value={"LS": '*', "PLACE": '*', "PL_POST": '*', "URN": '*', "PLACE_PROVIDER": '*'}, inplace=True)
            epi_merge = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_PRE'])

            epi_multi_row = epi_merge[epi_merge['CHILD'] == epi_merge['CHILD_PRE']]
            epi_has_B_U = epi_multi_row[epi_multi_row['RNE'].isin(['U', 'B'])]

            mask_ls = epi_has_B_U['LS'] == epi_has_B_U['LS_PRE']

            mask1 = epi_has_B_U['PLACE'] == epi_has_B_U['PLACE_PRE']
            mask2 = epi_has_B_U['PL_POST'] == epi_has_B_U['PL_POST_PRE']
            mask3 = epi_has_B_U['URN'] == epi_has_B_U['URN_PRE']
            mask4 = epi_has_B_U['PLACE_PROVIDER'] == epi_has_B_U['PLACE_PROVIDER_PRE']

            error_mask = mask_ls | (mask1 & mask2 & mask3 & mask4)

            error_list = epi_has_B_U[error_mask]['index'].to_list()
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_570():
    error = ErrorDefinition(
        code='570',
        description='The date that the child started to be missing or away from placement without authorisation is after the end of the collection year.',
        affected_fields=['MIS_START'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            error_mask = mis['MIS_START'] > collection_end

            return {'Missing': mis.index[error_mask].to_list()}

    return error, _validate


def validate_531():
    error = ErrorDefinition(
        code='531',
        description='A placement provider code of PR5 cannot be associated with placements P1.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'] == 'P1') & (epi['PLACE_PROVIDER'] == 'PR5')
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
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
            error_mask = (oc2['DOB'] + pd.offsets.DateOffset(years=10) > collection_end) & oc2['CONVICTED'].notna()
            return {'OC2': oc2.index[error_mask].to_list()}

    return error, _validate


def validate_620():
    error = ErrorDefinition(
        code='620',
        description='Child has been recorded as a mother, but date of birth shows that the mother is under 11 years of age.',
        affected_fields=['DOB', 'MOTHER'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            hea = dfs['Header']
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            hea['DOB'] = pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')

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
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(1)
            m_epi = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_NEXT'])
            m_epi = m_epi[m_epi['CHILD'] == m_epi['CHILD_NEXT']]

            mask_is_X1 = m_epi['REC'] == 'X1'
            mask_null_place_chg = m_epi['REASON_PLACE_CHANGE'].isna()
            mask_place_not_T = ~m_epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])
            mask_next_is_PBTU = m_epi['RNE_NEXT'].isin(['P', 'B', 'T', 'U'])
            mask_next_place_not_T = ~m_epi['PLACE_NEXT'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])

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
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['P1', 'R2', 'R5'])) & (epi['PLACE_PROVIDER'] == 'PR2')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_527():
    error = ErrorDefinition(
        code='527',
        description='A placement provider code of PR1 cannot be associated with placements P1, R2 or R5.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['P1', 'R2', 'R5'])) & (epi['PLACE_PROVIDER'] == 'PR1')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_359():
    error = ErrorDefinition(
        code='359',
        description='Child being looked after following 18th birthday must be accommodated under section 20(5) of the Children Act 1989 in a community home.',
        affected_fields=['DEC', 'LS', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Header' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            hea = dfs['Header']
            hea['DOB'] = pd.to_datetime(hea['DOB'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)
            epi = epi.merge(hea, on='CHILD', how='left', suffixes=['', '_HEA'])

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
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)
            epi = epi[epi['DECOM'] < collection_start]

            grp_decom_by_child = epi.groupby(['CHILD'])['DECOM'].idxmin(skipna=True)
            min_decom = epi.loc[epi.index.isin(grp_decom_by_child), :]

            grp_last_decom_by_child = epi_last.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_last_decom = epi_last.loc[epi_last.index.isin(grp_last_decom_by_child), :]

            merged_co = min_decom.merge(max_last_decom, how='left', on=['CHILD', 'DECOM'], suffixes=['', '_PRE'],
                                        indicator=True)
            error_cohort = merged_co[merged_co['_merge'] == 'left_only']

            error_list = error_cohort['index'].to_list()
            error_list = list(set(error_list))
            error_list.sort()
            return {'Episodes': error_list}

    return error, _validate


def validate_354():
    error = ErrorDefinition(
        code='354',
        description="Date episode ceased must be on or before the end of the current collection year.",
        affected_fields=['DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            error_mask = epi['DECOM'] > collection_end
            error_list = epi.index[error_mask].to_list()
            return {'Episodes': error_list}

    return error, _validate


def validate_385():
    error = ErrorDefinition(
        code='385',
        description="Date episode ceased must be on or before the end of the current collection year.",
        affected_fields=['DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            error_mask = epi['DEC'] > collection_end
            error_list = epi.index[error_mask].to_list()
            return {'Episodes': error_list}

    return error, _validate


def validate_408():
    error = ErrorDefinition(
        code='408',
        description='Child is placed for adoption with a placement order, but no placement order has been recorded.',
        affected_fields=['PLACE', 'LS'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = epi['PLACE'].isin(['A5', 'A6']) & (epi['LS'] != 'E1')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_380():
    error = ErrorDefinition(
        code='380',
        description='A period of care cannot start with a temporary placement.',
        affected_fields=['PLACE', 'RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])) & (~epi['RNE'].isin(['P', 'B']))
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_381():
    error = ErrorDefinition(
        code='381',
        description='A period of care cannot end with a temporary placement.',
        affected_fields=['PLACE', 'REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            error_mask = (epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])) & (epi['REC'] != 'X1') & (
                epi['REC'].notna())
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

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(1)

            merge_epi = epi.merge(epi, how='inner', left_on='LAG_INDEX', right_on='level_0', suffixes=['', '_PRE'])
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
        affected_fields=['RNE', 'DECOM'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)

            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)

            m_epi = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_PREV'])

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
        "G": {"Desc": "The distance in first episode does not match open episode at end of last year.",
              "Fields": 'PL_DISTANCE'},
        "H": {"Desc": "The placement LA in first episode does not match open episode at end of last year.",
              "Fields": 'PL_LA'},
        "J": {"Desc": "The placement location in first episode does not match open episode at end of last year.",
              "Fields": 'PL_LOCATION'},
    }
    error = ErrorDefinition(
        code='503' + subval,
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
            epi_last['DEC'] = pd.to_datetime(epi_last['DEC'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)

            first_ep_inds = epi.groupby(['CHILD'])['DECOM'].idxmin(skipna=True)
            min_decom = epi.loc[first_ep_inds, :]

            last_ep_inds = epi_last.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
            max_last_decom = epi_last.loc[last_ep_inds, :]

            merged_co = min_decom.merge(max_last_decom, how='inner', on=['CHILD'], suffixes=['', '_PRE'])

            this_one = Gen_503_dict[subval]['Fields']
            pre_one = this_one + '_PRE'

            if subval == 'G':
                err_mask = abs(merged_co[this_one].astype(float) - merged_co[pre_one].astype(float)) >= 0.2
            else:
                err_mask = merged_co[this_one].astype(str) != merged_co[pre_one].astype(str)
            err_mask = err_mask & merged_co['DEC_PRE'].isna()

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


def validate_503G():
    return validate_503_Generic('G')


def validate_503H():
    return validate_503_Generic('H')


def validate_503J():
    return validate_503_Generic('J')


def validate_526():
    error = ErrorDefinition(
        code='526',
        description='Child is missing a placement provider code for at least one episode.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
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
            if subval in ['370', '371', '372', '373', '374']:
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


def validate_529():
    error = ErrorDefinition(
        code='529',
        description='Placement provider code of PR3 cannot be associated with placements P1, A3 to A6, K1, K2 and U1 to U6 as these placements cannot be provided by other public organisations.',
        affected_fields=['PLACE', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            code_list_placement_type = ['A3', 'A4', 'A5', 'A6', 'K1', 'K2', 'P1', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6']
            error_mask = epi['PLACE'].isin(code_list_placement_type) & (epi['PLACE_PROVIDER'] == 'PR3')
            return {'Episodes': epi.index[error_mask].to_list()}

    return error, _validate


def validate_383():
    error = ErrorDefinition(
        code='383',
        description='A child in a temporary placement must subsequently return to his/her normal placement.',
        affected_fields=['PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)

            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)
            epi['LAG_INDEX'] = epi['level_0'].shift(-1)
            epi['LEAD_INDEX'] = epi['level_0'].shift(1)

            m_epi = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG_INDEX', suffixes=['', '_TOP'])
            m_epi = m_epi.merge(epi, how='inner', left_on='level_0', right_on='LEAD_INDEX', suffixes=['', '_BOTM'])
            m_epi = m_epi[m_epi['CHILD'] == m_epi['CHILD_TOP']]
            m_epi = m_epi[m_epi['CHILD'] == m_epi['CHILD_BOTM']]
            m_epi = m_epi[m_epi['PLACE'].isin(['T0', 'T1', 'T2', 'T3', 'T4'])]

            mask1 = m_epi['RNE_BOTM'] != 'P'
            mask2 = m_epi['PLACE_BOTM'] != m_epi['PLACE_TOP']
            err_mask = mask1 | mask2
            err_list = m_epi['index'][err_mask].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


def validate_377():
    error = ErrorDefinition(
        code='377',
        description='Only two temporary placements coded as being due to holiday of usual foster carer(s) are ' +
                    'allowed in any 12- month period.',
        affected_fields=['PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.reset_index(inplace=True)

            potent_cohort = epi[epi['PLACE'] == 'T3']

            # Here I'm after the CHILD ids where there are more than 2 T3 placements.
            count_them = potent_cohort.groupby('CHILD')['CHILD'].count().to_frame(name='cc')
            count_them.reset_index(inplace=True)
            count_them = count_them[count_them['cc'] > 2]

            err_coh = epi[epi['CHILD'].isin(count_them['CHILD'])]
            err_coh = err_coh[err_coh['PLACE'] == 'T3']

            err_list = err_coh['index'].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


# !# Potential false negatives - if child has no missing periods in current year's Missing table nothing is flagged!
def validate_576():
    error = ErrorDefinition(
        code='576',
        description='There is an open missing/away from placement without authorisation period in ' +
                    'last year’s return and there is no corresponding period recorded at the start of ' +
                    'this year.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Missing' not in dfs or 'Missing_last' not in dfs:
            return {}
        else:
            mis = dfs['Missing']
            mis_l = dfs['Missing_last']
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')
            mis_l['MIS_START'] = pd.to_datetime(mis_l['MIS_START'], format='%d/%m/%Y', errors='coerce')

            mis.reset_index(inplace=True)
            mis['MIS_START'].fillna(pd.to_datetime('01/01/2099', format='%d/%m/%Y', errors='coerce'), inplace=True)
            min_mis = mis.groupby(['CHILD'])['MIS_START'].idxmin()
            mis = mis.loc[min_mis, :]

            open_mis_l = mis_l.query("MIS_END.isnull()")

            err_coh = mis.merge(open_mis_l, how='left', on='CHILD', suffixes=['', '_LAST'])
            err_coh = err_coh.query("(MIS_START != MIS_START_LAST) & MIS_START_LAST.notnull()")

            err_list = err_coh['index'].unique().tolist()
            err_list.sort()
            return {'Missing': err_list}

    return error, _validate


def validate_553():
    error = ErrorDefinition(
        code='553',
        description='Placement order has been granted but there is no date of decision that the child should ' +
                    'be placed for adoption.',
        affected_fields=['CHILD', 'DATE_PLACED', 'DATE_PLACED_CEASED', 'REASON_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            sho = dfs['PlacedAdoption']
            sho.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            epi_has_e1 = epi[epi['LS'] == 'E1']
            merge_w_sho = epi_has_e1.merge(sho, how='left', on='CHILD', suffixes=['_EP', '_PA'], indicator=True)

            # E1 episodes without a corresponding PlacedAdoption entry
            err_list_epi = merge_w_sho.query("(_merge == 'left_only')")['index_EP'].unique().tolist()

            # Open E1 Episodes where DATE_PLACED_CEASED or REASON_PLACED_CEASED is filled in
            epi_open_e1 = epi[(epi['LS'] == 'E1') & epi['DEC'].isna()]
            merge_w_sho2 = epi_open_e1.merge(sho, how='inner', on='CHILD', suffixes=['_EP', '_PA'])
            err_list_sho = merge_w_sho2['index_PA'][merge_w_sho2['DATE_PLACED_CEASED'].notna()
                                                    | merge_w_sho2['REASON_PLACED_CEASED'].notna()]
            err_list_sho = err_list_sho.unique().tolist()
            return {'Episodes': err_list_epi, 'PlacedAdoption': err_list_sho}

    return error, _validate


def validate_555():
    error = ErrorDefinition(
        code='555',
        description='Freeing order has been granted but there is no date of decision that the child should ' +
                    'be placed for adoption.',
        affected_fields=['CHILD', 'DATE_PLACED', 'DATE_PLACED_CEASED', 'REASON_PLACED_CEASED'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'PlacedAdoption' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            sho = dfs['PlacedAdoption']
            sho.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            # D1 episodes without a corresponding PlacedAdoption entry
            epi_has_d1 = epi[epi['LS'] == 'D1']
            merge_w_sho = epi_has_d1.merge(sho, how='left', on='CHILD', suffixes=['_EP', '_PA'], indicator=True)
            err_list_epi = merge_w_sho.query("_merge == 'left_only'")['index_EP'].unique().tolist()

            # Open D1 Episodes where DATE_PLACED_CEASED or REASON_PLACED_CEASED is filled in
            epi_open_d1 = epi[(epi['LS'] == 'D1') & epi['DEC'].isna()]
            merge_w_sho2 = epi_open_d1.merge(sho, how='inner', on='CHILD', suffixes=['_EP', '_PA'])
            err_list_sho = merge_w_sho2['index_PA'][merge_w_sho2['DATE_PLACED_CEASED'].notna()
                                                    | merge_w_sho2['REASON_PLACED_CEASED'].notna()]
            err_list_sho = err_list_sho.unique().tolist()
            return {'Episodes': err_list_epi, 'PlacedAdoption': err_list_sho}

    return error, _validate


def validate_382():
    error = ErrorDefinition(
        code='382',
        description='A child receiving respite care cannot be in a temporary placement.',
        affected_fields=['LS', 'PLACE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            err_list = epi.query("LS.isin(['V3', 'V4']) & PLACE.isin(['T0', 'T1', 'T2', 'T3', 'T4'])").index.tolist()
            return {'Episodes': err_list}

    return error, _validate


def validate_602():
    error = ErrorDefinition(
        code='602',
        description='The episode data submitted for this child does not show that he/she was adopted during the year.',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'AD1' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            ad1 = dfs['AD1']
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            mask1 = (epi['DEC'] <= collection_end) & (epi['DEC'] >= collection_start)
            mask2 = epi['REC'].isin(['E11', 'E12'])
            adoption_eps = epi[mask1 & mask2]

            adoption_fields = ['DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR']

            err_list = (ad1
                        .reset_index()
                        .merge(adoption_eps, how='left', on='CHILD', indicator=True)
                        .query("_merge == 'left_only'")
                        .dropna(subset=adoption_fields, how='all')
                        .set_index('index')
                        .index
                        .unique()
                        .to_list())

            return {'AD1': err_list}

    return error, _validate


def validate_580():
    error = ErrorDefinition(
        code='580',
        description='Child is missing when cease being looked after but reason episode ceased not ‘E8’.',
        affected_fields=['REC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            mis = dfs['Missing']
            mis['MIS_END'] = pd.to_datetime(mis['MIS_END'], format='%d/%m/%Y', errors='coerce')
            mis['DOB'] = pd.to_datetime(mis['DOB'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')

            epi.reset_index(inplace=True)
            mis['BD18'] = mis['DOB'] + pd.DateOffset(years=18)

            m_coh = mis.merge(epi, how='inner', on='CHILD')
            m_coh = m_coh.query("(BD18 == MIS_END) & (MIS_END == DEC) & DEC.notnull()")
            err_list = m_coh.query("REC != 'E8'")['index'].unique().tolist()
            err_list.sort()
            return {'Episodes': err_list}

    return error, _validate


def validate_575():
    error = ErrorDefinition(
        code='575',
        description='If the placement from which the child goes missing/away from placement without ' +
                    'authorisation ends, the missing/away from placement without authorisation period in ' +
                    'the missing module must also have an end date.',
        affected_fields=['MIS_END'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs or 'Missing' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            mis = dfs['Missing']

            mis.reset_index(inplace=True)

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            mis['MIS_START'] = pd.to_datetime(mis['MIS_START'], format='%d/%m/%Y', errors='coerce')

            m_coh = epi.merge(mis, how='inner', on='CHILD') \
                .query("(MIS_START >= DECOM) & (MIS_START <= DEC) & MIS_END.isnull() & DEC.notnull()")

            err_list = m_coh['index'].unique().tolist()
            err_list.sort()
            return {'Missing': err_list}

            return {'Episodes': Episodes_errs,
                    'AD1': AD1_errs}

    return error, _validate


def validate_1012():
    error = ErrorDefinition(
        code='1012',
        description='No other data should be returned for OC3 children who had no episodes in the current year',
        affected_fields=['CHILD'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}

        epi = dfs['Episodes']

        error_dict = {}
        for table in ['PlacedAdoption', 'Missing', 'Reviews', 'AD1', 'PrevPerm', 'OC2']:
            if table in dfs.keys():
                df = dfs[table]
                error_dict[table] = (
                    df
                        .reset_index()
                        .merge(epi, how='left', on='CHILD', indicator=True)
                        .query("_merge == 'left_only'")
                    ['index'].unique()
                        .tolist()
                )
        return error_dict

    return error, _validate


def validate_432():
    error = ErrorDefinition(
        code='432',
        description='The child ceased to be looked after at the end of the previous episode but the reason for ' +
                    'the new episode is not started to be looked after.',
        affected_fields=['RNE'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            rec_vals1 = ['E2', 'E3', 'E4A', 'E4B', 'E5', 'E6', 'E7', 'E8', 'E9', 'E11']
            rec_vals2 = ['E12', 'E13', 'E14', 'E15', 'E16', 'E17', 'E41', 'E45', 'E46', 'E47', 'E48']
            rec_vals = rec_vals1 + rec_vals2

            epi['LAG'] = epi['level_0'].shift(-1)

            err_co = epi.merge(epi, how='inner', left_on='level_0', right_on='LAG', suffixes=['', '_PRE']) \
                .query("CHILD == CHILD_PRE & REC_PRE.isin(@rec_vals) & RNE != 'S'")

            err_list = err_co['index'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_331():
    error = ErrorDefinition(
        code='331',
        description='Date of matching child and adopter(s) should be the same as, or prior to, the date of placement of adoption.',
        affected_fields=['DATE_MATCH',  # AD1
                         'DECOM', 'REC'],  # Episodes
    )

    def _validate(dfs):
        if 'AD1' not in dfs or 'Episodes' not in dfs:
            return {}
        else:
            adt = dfs['AD1']
            eps = dfs['Episodes']

            # Save indexes of each table so we can retreive the original positions in each for our error rows
            adt['AD1_index'] = adt.index
            eps['Episodes_index'] = eps.index

            adt['DATE_MATCH'] = pd.to_datetime(adt['DATE_MATCH'], format='%d/%m/%Y', errors='coerce')
            eps['DECOM'] = pd.to_datetime(eps['DECOM'], format='%d/%m/%Y', errors='coerce')

            # Only keep the episodes where <Adopted> = 'Y'
            adoption_eps = eps[eps['REC'].isin(['E11', 'E12'])]

            # Merge AD1 and Episodes so we can compare DATE_MATCH and DECOM
            adoption_eps = adoption_eps.merge(adt, on='CHILD')

            # A child cannot be placed for adoption before the child has been matched with prospective adopter(s).
            error_mask = adoption_eps['DATE_MATCH'] > adoption_eps['DECOM']

            # Get the rows of each table where the dates clash
            AD1_errs = list(adoption_eps.loc[error_mask, 'AD1_index'].unique())
            Episodes_errs = list(adoption_eps.loc[error_mask, 'Episodes_index'].unique())

            return {'AD1': AD1_errs,
                    'Episodes': Episodes_errs}

    return error, _validate


def validate_362():
    error = ErrorDefinition(
        code='362',
        description='Emergency protection order (EPO) lasted longer than 21 days',
        affected_fields=['DECOM', 'LS', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            epi['LAG'] = epi['level_0'] - 1

            epi['DEC'].fillna(collection_end, inplace=True)

            err_co = epi.merge(epi, how='left', left_on='level_0', right_on='LAG', suffixes=['', '_NEXT']) \
                .query("LS == 'L2'")

            # Create a partition "FLOWS" for two or more separate flow sequences of L2 code dates within the same child.
            # when the dec / decom_next dates stop flowing or the child id changes
            # the cumsum is incremented this can then be used as the partition.
            err_co['FLOWS'] = (err_co['DEC'] == err_co['DECOM_NEXT']) & (err_co['CHILD'] == err_co['CHILD_NEXT'])
            err_co['FLOWS'] = err_co['FLOWS'].shift(1)
            err_co['FLOWS'].fillna(False, inplace=True)
            err_co['FLOWS'] = ~err_co['FLOWS']
            err_co['FLOWS'] = err_co['FLOWS'].astype(int).cumsum()

            # Calc the min decom and max dec in each group so the days between them can be calculated.
            grp_decom = err_co.groupby(['CHILD', 'FLOWS'])['DECOM'].min().to_frame(name='MIN_DECOM').reset_index()
            grp_dec = err_co.groupby(['CHILD', 'FLOWS'])['DEC'].max().to_frame(name='MAX_DEC').reset_index()
            grp_len_l2 = grp_decom.merge(grp_dec, how='inner', on=['CHILD', 'FLOWS'])

            # Throw out anything <= 21 days.
            grp_len_l2['DAY_DIF'] = (grp_len_l2['MAX_DEC'] - grp_len_l2['MIN_DECOM']).dt.days
            grp_len_l2 = grp_len_l2.query("DAY_DIF > 21").copy()

            # Inner join back to the err_co and get the original index out.
            err_co['MERGE_KEY'] = err_co['CHILD'].astype(str) + err_co['FLOWS'].astype(str)
            grp_len_l2['MERGE_KEY'] = grp_len_l2['CHILD'].astype(str) + grp_len_l2['FLOWS'].astype(str)
            err_final = err_co.merge(grp_len_l2, how='inner', on=['MERGE_KEY'], suffixes=['', '_IG'])

            err_list = err_final['index'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_361():
    error = ErrorDefinition(
        code='361',
        description='Police protection legal status lasted longer than maximum 72 hours allowed ' +
                    'in the Children Act 1989.',
        affected_fields=['DECOM', 'LS', 'DEC'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']

            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi['DEC'] = pd.to_datetime(epi['DEC'], format='%d/%m/%Y', errors='coerce')
            collection_end = pd.to_datetime(dfs['metadata']['collection_end'], format='%d/%m/%Y', errors='coerce')

            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi.reset_index(inplace=True)
            epi.reset_index(inplace=True)

            epi['LAG'] = epi['level_0'] - 1

            epi['DEC'].fillna(collection_end, inplace=True)

            err_co = epi.merge(epi, how='left', left_on='level_0', right_on='LAG', suffixes=['', '_NEXT']) \
                .query("LS == 'L1'")

            # Create a partition "FLOWS" for two or more separate flow sequences of L2 code dates within the same child.
            # when the dec / decom_next dates stop flowing or the child id changes
            # the cumsum is incremented this can then be used as the partition.
            err_co['FLOWS'] = (err_co['DEC'] == err_co['DECOM_NEXT']) & (err_co['CHILD'] == err_co['CHILD_NEXT'])
            err_co['FLOWS'] = err_co['FLOWS'].shift(1)
            err_co['FLOWS'].fillna(False, inplace=True)
            err_co['FLOWS'] = ~err_co['FLOWS']
            err_co['FLOWS'] = err_co['FLOWS'].astype(int).cumsum()

            # Calc the min decom and max dec in each group so the days between them can be calculated.
            grp_decom = err_co.groupby(['CHILD', 'FLOWS'])['DECOM'].min().to_frame(name='MIN_DECOM').reset_index()
            grp_dec = err_co.groupby(['CHILD', 'FLOWS'])['DEC'].max().to_frame(name='MAX_DEC').reset_index()
            grp_len_l2 = grp_decom.merge(grp_dec, how='inner', on=['CHILD', 'FLOWS'])

            # Throw out anything <= 3 days.
            grp_len_l2['DAY_DIF'] = (grp_len_l2['MAX_DEC'] - grp_len_l2['MIN_DECOM']).dt.days
            grp_len_l2 = grp_len_l2.query("DAY_DIF > 3").copy()

            # Inner join back to the err_co and get the original index out.
            err_co['MERGE_KEY'] = err_co['CHILD'].astype(str) + err_co['FLOWS'].astype(str)
            grp_len_l2['MERGE_KEY'] = grp_len_l2['CHILD'].astype(str) + grp_len_l2['FLOWS'].astype(str)
            err_final = err_co.merge(grp_len_l2, how='inner', on=['MERGE_KEY'], suffixes=['', '_IG'])

            err_list = err_final['index'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_435():
    error = ErrorDefinition(
        code='435',
        description='Reason for new episode is that child’s placement has changed but not the legal status, ' +
                    'but this is not reflected in the episode data recorded.',
        affected_fields=['LS', 'PLACE', 'PL_POST', 'URN', 'PLACE_PROVIDER'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            epi = dfs['Episodes']
            epi['DECOM'] = pd.to_datetime(epi['DECOM'], format='%d/%m/%Y', errors='coerce')
            epi.sort_values(['CHILD', 'DECOM'], inplace=True)
            epi['idx_orig'] = epi.index
            epi.reset_index(inplace=True)
            epi['idx_ordered'] = epi.index
            epi['idx_previous'] = epi.index + 1

            err_co = epi.merge(epi, how='inner', left_on='idx_ordered', right_on='idx_previous', suffixes=['', '_PRE']) \
                .query("RNE.isin(['P', 'T']) & CHILD == CHILD_PRE") \
                .query("(LS != LS_PRE) | ((PLACE == PLACE_PRE) & (PL_POST == PL_POST_PRE) & (URN == URN_PRE) & " +
                       "(PLACE_PROVIDER == PLACE_PROVIDER_PRE))")

            err_list = err_co['idx_orig'].unique().tolist()
            err_list.sort()

            return {'Episodes': err_list}

    return error, _validate


def validate_624():
    error = ErrorDefinition(
        code='624',
        description="Date of birth of the first child contradicts the date of birth of the first child previously " +
                    "recorded.",
        affected_fields=['MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            hea = dfs['Header']
            hea_pre = dfs['Header_last']
            hea['orig_idx'] = hea.index

            err_co = hea.merge(hea_pre, how='inner', on='CHILD', suffixes=['', '_PRE']) \
                .query("MC_DOB_PRE.notna() & (MC_DOB != MC_DOB_PRE)")

            err_list = err_co['orig_idx'].unique().tolist()
            err_list.sort()
            return {'Header': err_list}

    return error, _validate


def validate_626():
    error = ErrorDefinition(
        code='626',
        description="Child was reported as a mother but the date of birth of the first child is before the current " +
                    "year which contradicts with the mother status recorded last year.",
        affected_fields=['MOTHER', 'MC_DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs or 'Header_last' not in dfs:
            return {}
        else:
            header = dfs['Header']
            header_prev = dfs['Header_last']
            collection_start = dfs['metadata']['collection_start']
            header['MC_DOB'] = pd.to_datetime(header['MC_DOB'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(collection_start, format='%d/%m/%Y', errors='coerce')
            header['orig_idx'] = header.index
            header = header.query("MC_DOB.notna()")
            merged = header.merge(header_prev, how='inner', on='CHILD', suffixes=['', '_PRE'])
            merged['MOTHER'] = pd.to_numeric(merged['MOTHER'], errors='coerce')
            merged['MOTHER_PRE'] = pd.to_numeric(merged['MOTHER_PRE'], errors='coerce')
            err_co = merged[
                (merged['MOTHER'] == 1)
                & (merged['MOTHER_PRE'] == 0)
                & (merged['MC_DOB'] < collection_start)
                ]
            err_list = err_co['orig_idx'].unique().tolist()
            err_list.sort()
            return {'Header': err_list}

    return error, _validate


def validate_104():
    error = ErrorDefinition(
        code='104',
        description='Date for Unaccompanied Asylum-Seeking Children (UASC) status ceased is not a valid date.',
        affected_fields=['DUC'],
    )

    def _validate(dfs):
        if 'UASC' not in dfs:
            return {}
        else:
            uasc = dfs['UASC']
            uasc['DUC_dt'] = pd.to_datetime(uasc['DUC'], format='%d/%m/%Y', errors='coerce')
            collection_start = pd.to_datetime(dfs['metadata']['collection_start'], format='%d/%m/%Y', errors='coerce')
            mask = (uasc['DUC_dt'].isna() & uasc['DUC'].notna()) | (uasc['DUC_dt'] < collection_start)

            return {'UASC': uasc.index[mask].to_list()}

    return error, _validate


# !# False positives if child was UASC in last 2 years but data not provided
def validate_392B():
    error = ErrorDefinition(
        code='392B',
        description='Child is looked after but no postcodes are recorded. [NOTE: This check may result in false '
                    'positives for children formerly UASC, particularly if current & prior year UASC data not loaded]',
        affected_fields=['HOME_POST', 'PL_POST'],
    )

    def _validate(dfs):
        # Will also use Header/UASC and/or Header_last/UASC_last for former UASC status
        if 'Episodes' not in dfs:
            return {}
        else:
            # If <LS> not = 'V3' or 'V4' and <UASC> = '0' and <COLLECTION YEAR> - 1 <UASC> = '0' and <COLLECTION YEAR> - 2 <UASC> = '0' then <HOME_POST> and <PL_POST> should be provided.
            epi = dfs['Episodes']
            epi['original_index'] = epi.index

            # Remove any children with evidence of former UASC status
            header = pd.DataFrame()
            if 'Header' in dfs:
                header_current = dfs['Header']
                header = pd.concat((header, header_current), axis=0)
            elif 'UASC' in dfs:
                uasc = dfs['UASC']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'Header_last' in dfs:
                header = pd.concat((header, dfs['Header_last']), axis=0)
            elif 'UASC_last' in dfs:
                uasc = dfs['UASC_last']
                uasc = uasc.loc[uasc.drop('CHILD', axis='columns').notna().any(axis=1), ['CHILD']].copy()
                uasc.loc[:, 'UASC'] = '1'
                header = pd.concat((header, uasc), axis=0)

            if 'UASC' in header.columns:
                header = header[header.UASC == '1'].drop_duplicates('CHILD')
                epi = (epi
                       .merge(header[['CHILD']], how='left', on='CHILD', indicator=True)
                       .query("_merge == 'left_only'"))

            # Remove episodes where LS is V3/V4
            epi = epi.query("(~LS.isin(['V3','V4']))")

            # Remove episodes with postcodes filled in
            epi = epi.query("(HOME_POST.isna() | PL_POST.isna())")

            # Get error indices
            err_list = epi['original_index'].sort_values().tolist()

            return {'Episodes': err_list}

    return error, _validate


def validate_303():
    error = ErrorDefinition(
        code='303',
        description="If date Unaccompanied Asylum-Seeking Child (UASC) status ceased is not null, UASC status must be coded 1.",
        affected_fields=['DUC', 'UASC']
    )

    def _validate(dfs):
        if ('UASC' not in dfs) or ('Header' not in dfs):
            return {}
        elif 'UASC' not in dfs['Header'].columns:
            return {}
        else:
            uasc = dfs['UASC']
            header = dfs['Header']

            # merge
            uasc.reset_index(inplace=True)
            header.reset_index(inplace=True)

            merged = header.merge(uasc, how='left', on='CHILD', suffixes=['_er', '_sc'])

            merged['UASC'] = pd.to_numeric(merged['UASC'], errors='coerce')

            # If <DUC> provided, then <UASC> must be '1'
            error_mask = merged['DUC'].notna() & (merged['UASC'] != 1)

            uasc_error_locs = merged.loc[error_mask, 'index_sc']
            header_error_locs = merged.loc[error_mask, 'index_er']

            return {'UASC': uasc_error_locs.tolist(),
                    'Header': header_error_locs.tolist()}

    return error, _validate
