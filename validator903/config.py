from .validators import *

"""
Column names for each 903 file.

These are used in two places:
- Checking that the uploaded files match and identifying which CSV file is which (when CSVs are selected).
- Constructing CSV files from provided XML (when XML is selected)
"""
column_names = {
    'Header': ['CHILD', 'SEX', 'DOB', 'ETHNIC', 'UPN', 'MOTHER', 'MC_DOB'],
    'Episodes': ['CHILD', 'DECOM', 'RNE', 'LS', 'CIN', 'PLACE', 'PLACE_PROVIDER', 'DEC', 'REC', 'REASON_PLACE_CHANGE', 'HOME_POST', 'PL_POST', 'URN'],
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

"""
List of all configured errors for validation.

These all should have return type (Error, Dict[str, DataFrame])
"""
configured_errors = [
    validate_101(),
    validate_102(),
    validate_103(),
    validate_114(),
    validate_120(),
    validate_131(),
    validate_132(),
    validate_141(),
    validate_112(),
    validate_113(),
    validate_115(),
    validate_116(),
    validate_119(),
    validate_134(),
    validate_143(),
    validate_144(),
    validate_145(),
    validate_146(),
    validate_147(),
    validate_149(),
    validate_164(),
    validate_167(),
    validate_168(),
    validate_169(),
    validate_171(),
    validate_175(),
    validate_176(),
    validate_177(),
    validate_178(),
    validate_179(),
    validate_182(),
    validate_196(),
    validate_213(),
    validate_388(),
    validate_392c(),
    validate_611(),
    validate_631(),
    validate_1006(),
    validate_1009(),
    validate_142(),
    validate_148(),
    validate_366(),
    validate_222(),
    validate_214(),
]
