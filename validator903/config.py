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
    'OC3': ['CHILD', 'DOB', 'IN_TOUCH', 'ACTIV', 'ACCOM'],
    'AD1': ['CHILD', 'DOB', 'DATE_INT', 'DATE_MATCH', 'FOSTER_CARE', 'NB_ADOPTR', 'SEX_ADOPTR', 'LS_ADOPTR'],
    'PlacedAdoption': ['CHILD', 'DOB', 'DATE_PLACED', 'DATE_PLACED_CEASED', 'REASON_PLACED_CEASED'],
}

"""
List of all configured errors for validation.

These all should have return type (Error, Dict[str, DataFrame])
"""
configured_errors = [
    validate_101(),
    validate_143(),
    validate_103(),
    validate_102(),
    validate_392c(),
]