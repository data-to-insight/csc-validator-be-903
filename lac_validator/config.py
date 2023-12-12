"""
Column names for each 903 file.

These are used in two places:
- Checking that the uploaded files match and identifying which CSV file is which (when CSVs are selected).
- Constructing CSV files from provided XML (when XML is selected)
"""
column_names = {
    "Header": ["CHILD", "SEX", "DOB", "ETHNIC", "UPN", "MOTHER", "MC_DOB"],
    "Episodes": [
        "CHILD",
        "DECOM",
        "RNE",
        "LS",
        "CIN",
        "PLACE",
        "PLACE_PROVIDER",
        "DEC",
        "REC",
        "REASON_PLACE_CHANGE",
        "HOME_POST",
        "PL_POST",
        "URN",
    ],
    "Reviews": ["CHILD", "DOB", "REVIEW", "REVIEW_CODE"],
    "UASC": ["CHILD", "SEX", "DOB", "DUC"],
    "OC2": [
        "CHILD",
        "DOB",
        "SDQ_SCORE",
        "SDQ_REASON",
        "CONVICTED",
        "HEALTH_CHECK",
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ],
    "OC3": ["CHILD", "DOB", "IN_TOUCH", "ACTIV", "ACCOM"],
    "AD1": [
        "CHILD",
        "DOB",
        "DATE_INT",
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ],
    "PlacedAdoption": [
        "CHILD",
        "DOB",
        "DATE_PLACED",
        "DATE_PLACED_CEASED",
        "REASON_PLACED_CEASED",
    ],
    # Note: for PrevPerm, LA_PERM will usually be blank and shouldn't be used directly
    "PrevPerm": ["CHILD", "DOB", "PREV_PERM", "LA_PERM", "DATE_PERM"],
    "Missing": ["CHILD", "DOB", "MISSING", "MIS_START", "MIS_END"],
    "SWEpisodes": ["CHILD", "DOB", "SW_ID", "SW_DECOM", "SW_DEC", "SW_REASON"],
}
