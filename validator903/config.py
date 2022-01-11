from .validators import *

"""
Column names for each 903 file.

These are used in two places:
- Checking that the uploaded files match and identifying which CSV file is which (when CSVs are selected).
- Constructing CSV files from provided XML (when XML is selected)
"""
column_names = {
    'Header': ['CHILD', 'SEX', 'DOB', 'ETHNIC', 'UPN', 'MOTHER', 'MC_DOB', 'UASC'],
    'Episodes': ['CHILD', 'DECOM', 'RNE', 'LS', 'CIN', 'PLACE', 'PLACE_PROVIDER', 'DEC', 'REC', 'REASON_PLACE_CHANGE',
                 'HOME_POST', 'PL_POST', 'URN'],
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

every_single_error_code = "101,102,103,104,105,112,113,114,115,116,117,118,119,120,131,132,133,134,141,142,143,144," \
                          "145,146,147,148,149,151,153,157,158,159,164,165,166,167,168,169,171,174,175,176,177,178," \
                          "179,180,181,182,185,186,187,188,189,190,191,192,193,196,198,199,1000,1001,1002,1004," \
                          "1005,1006,1007,1008,1009,1010,1011,1012,1014,1015,NoE,357,388,502,184,1003,202,203,204," \
                          "205A,205B,205C,205D,207,208,209,210,213,214,215,217,218,219,221,224,225,226,227,228,229," \
                          "301,302,303,304,331,333,334,335,336,344,345,351,352,353,354,355,356,358,359,361,362,363," \
                          "364,365,366,367,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387," \
                          "389,390,391,392a,392b,392c,393,398,399,3001,406,407,408,411,420,426,431,432,433,434,435," \
                          "436,437,440,441,442,445,446,451,452,453,501,504,511,514,516,517,518,519,520,521,522,523," \
                          "524,525,526,527,528,529,530,531,542,543,544,545,546,547,550,551,552,553,554,555,556,557," \
                          "558,559,560,561,562,563,564,565,566,567,570,571,574,575,576,577,578,579,580,586,601,602," \
                          "607,611,612,620,621,624,625,626,628,630,631,632,633,634,635,503A,503B,503C,503D,503E,503F," \
                          "503G,503H,503J,460,197A,197B,222"
every_single_error_code = sorted(tuple(every_single_error_code.lower().split(',')))

stage_1_error_codes = "101,102,103,104,105,112,113,114,115,116,117,118,119,120,131,132,133,134,141,142,143,144,145," \
                      "146,147,148,149,151,153,157,158,159,164,165,166,167,168,169,171,174,175,176,177,178,179,180," \
                      "181,182,185,186,187,188,189,190,191,192,193,196,197A,197B,198,199,1000,1001,1002,1004,1005," \
                      "1006,1007,1008,1009,1010,1011,1012,1014,1015,NOE,357,388,502"
stage_1_error_codes = sorted(tuple(stage_1_error_codes.lower().split(',')))

stage_2_error_codes = sorted(tuple(set(every_single_error_code) - set(stage_1_error_codes)))

"""
List of all configured errors for validation.

These all should have return type (Error, Dict[str, DataFrame])
"""
configured_errors = sorted([
    validate_198(),
    validate_552(),
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
    validate_159(),
    validate_153(),
    validate_164(),
    validate_166(),
    validate_167(),
    validate_168(),
    validate_169(),
    validate_171(),
    validate_174(),
    validate_175(),
    validate_176(),
    validate_177(),
    validate_178(),
    validate_184(),
    validate_179(),
    validate_180(),
    validate_181(),
    validate_182(),
    validate_192(),
    validate_193(),
    validate_196(),
    validate_197a(),
    validate_202(),
    validate_207(),
    validate_208(),
    validate_204(),
    validate_203(),
    validate_213(),
    validate_3001(),
    validate_352(),
    validate_356(),
    validate_387(),
    validate_386(),
    validate_388(),
    validate_389(),
    validate_392c(),
    validate_530(),
    validate_393(),
    validate_411(),
    validate_420(),
    validate_433(),
    validate_437(),
    validate_452(),
    validate_453(),
    validate_611(),
    validate_612(),
    validate_621(),
    validate_631(),
    validate_1004(),
    validate_1005(),
    validate_1006(),
    validate_1009(),
    validate_1010(),
    validate_1015(),
    validate_142(),
    validate_148(),
    validate_151(),
    validate_366(),
    validate_222(),
    validate_214(),
    validate_628(),
    validate_355(),
    validate_586(),
    validate_556(),
    validate_630(),
    validate_501(),
    validate_502(),
    validate_NoE(),
    validate_567(),
    validate_571(),
    validate_304(),
    validate_333(),
    validate_1011(),
    validate_574(),
    validate_564(),
    validate_566(),
    validate_570(),
    validate_531(),
    validate_542(),
    validate_620(),
    validate_225(),
    validate_353(),
    validate_528(),
    validate_527(),
    validate_359(),
    validate_562(),
    validate_354(),
    validate_385(),
    validate_408(),
    validate_380(),
    validate_381(),
    validate_504(),
    validate_436(),
    validate_431(),
    validate_503A(),
    validate_503B(),
    validate_503C(),
    validate_503D(),
    validate_503E(),
    validate_503F(),
    validate_503G(),
    validate_503H(),
    validate_503J(),
    validate_523(),
    validate_526(),
    validate_445(),
    validate_446(),
    validate_441(),
    validate_440(),
    validate_550(),
    validate_516(),
    validate_363(),
    validate_364(),
    validate_365(),
    validate_367(),
    validate_370(),
    validate_371(),
    validate_372(),
    validate_373(),
    validate_374(),
    validate_375(),
    validate_376(),
    validate_379(),
    validate_383(),
    validate_529(),
    validate_557(),
    validate_551(),
    validate_524(),
    validate_511(),
    validate_547(),
    validate_558(),
    validate_563(),
    validate_565(),
    validate_635(),
    validate_377(),
    validate_518(),
    validate_517(),
    validate_576(),
    validate_344(),
    validate_345(),
    validate_384(),
    validate_390(),
    validate_398(),
    validate_451(),
    validate_520(),
    validate_522(),
    validate_553(),
    validate_555(),
    validate_544(),
    validate_382(),
    validate_602(),
    validate_158(),
    validate_580(),
    validate_575(),
    validate_133(),
    validate_1012(),
    validate_525(),
    validate_432(),
    validate_634(),
    validate_442(),
    validate_331(),
    validate_217(),
    validate_519(),
    validate_378(),
    validate_1007(),
    validate_215(),
    validate_399(),
    validate_189(),
    validate_226(),
    validate_358(),
    validate_362(),
    validate_361(),
    validate_407(),
    validate_335(),
    validate_209(),
    validate_435(),
    validate_607(),
    validate_185(),
    validate_186(),
    validate_187(),
    validate_188(),
    validate_190(),
    validate_191(),
    validate_210(),
    validate_165(),
    validate_1014(),
    validate_392B(),
    validate_117(),
    validate_118(),
    validate_357(),
    validate_197B(),
    validate_157(),
    validate_632(),
    validate_105(),
])

errors = {e[0].code: e for e in configured_errors}
