# The code in this file was used to split the validators.py and test_validators.py in the 903 validator into this new format
# where there is one file per rule.
# This is where the tool rewrite started.

import re

from black import FileMode, format_str

fake_uasc_205 = """fake_uasc_205 = pd.DataFrame([
        {'CHILD': '101', 'DOB': '28/10/2004', 'DUC': pd.NA},#Pass C
        {'CHILD': '102', 'DOB': '04/06/2004', 'DUC': pd.NA},#Pass A
        {'CHILD': '103', 'DOB': '03/03/2002', 'DUC': '10/07/2020'},#Fail A
        {'CHILD': '104', 'DOB': '28/03/2003', 'DUC': '14/05/2021'},#Fail A
        {'CHILD': '105', 'DOB': '16/04/2001', 'DUC': '16/04/2019'},#Fail B
        {'CHILD': '106', 'DOB': '04/11/2004', 'DUC': '16/06/2021'},#Fail B
        {'CHILD': '107', 'DOB': '23/07/2002', 'DUC': '23/07/2020'},#Pass B
        {'CHILD': '108', 'DOB': '19/02/2003', 'DUC': pd.NA},#Fail C
        {'CHILD': '109', 'DOB': '14/06/2003', 'DUC': '14/06/2021'},#Fail D
        {'CHILD': '110', 'DOB': '14/06/2003', 'DUC': pd.NA},  # Fail D
    ])"""

fake_uasc_prev_205 = """fake_uasc_prev_205 = pd.DataFrame([
        {'CHILD': '101', 'DOB': '28/10/2004', 'DUC': pd.NA},#Pass C
        {'CHILD': '102', 'DOB': '04/06/2004', 'DUC': '20/01/2020'},#Pass A
        {'CHILD': '103', 'DOB': '03/03/2002', 'DUC': '10/07/2020'},#Fail A
        {'CHILD': '104', 'DOB': '28/03/2003', 'DUC': '14/05/2021'},#Fail A
        {'CHILD': '105', 'DOB': '16/04/2001', 'DUC': '16/04/2019'},#Fail B
        {'CHILD': '106', 'DOB': '04/11/2004', 'DUC': '04/11/2023'},#Fail B
        {'CHILD': '107', 'DOB': '23/07/2002', 'DUC': '23/07/2020'},#Pass B
        {'CHILD': '108', 'DOB': '19/02/2003', 'DUC': '19/02/2021'},#Fail C
        {'CHILD': '109', 'DOB': '14/06/2003', 'DUC': '14/06/2021'},#Fail D
        {'CHILD': '110', 'DOB': '14/06/2003', 'DUC': '14/06/2021'},  # Fail D
    ])"""

fake_header_205 = """fake_header_205 = pd.DataFrame([
        {'CHILD': '101', 'DOB': '28/10/2004', 'UASC': '0'},#Pass C
        {'CHILD': '108', 'DOB': '19/02/2003', 'UASC': '0'},#Fail C
        {'CHILD': '109', 'DOB': '14/06/2003', 'UASC': '1'},#Fail D
        {'CHILD': '102', 'DOB': '04/06/2004', 'UASC': '0'},#Pass A
        {'CHILD': '103', 'DOB': '03/03/2002', 'UASC': '0'},#Fail A
        {'CHILD': '104', 'DOB': '28/03/2003', 'UASC': '0'},#Fail A
        {'CHILD': '105', 'DOB': '16/04/2001', 'UASC': '1'},#Fail B
        {'CHILD': '106', 'DOB': '04/11/2004', 'UASC': '1'},#Fail B
        {'CHILD': '107', 'DOB': '23/07/2002', 'UASC': '1'},#Pass B
        {'CHILD': '110', 'DOB': '03/03/2002', 'UASC': '0'},
    ])"""

fake_prev_header_205 = """prev_fake_header_205 = pd.DataFrame([
        {'CHILD': '102', 'DOB': '04/06/2004', 'UASC': '1'},#Pass A
        {'CHILD': '103', 'DOB': '03/03/2002', 'UASC': '1'},#Fail A
        {'CHILD': '104', 'DOB': '28/03/2003', 'UASC': '1'},#Fail A
        {'CHILD': '101', 'DOB': '28/10/2004', 'UASC': '0'},#Pass C
        {'CHILD': '105', 'DOB': '16/04/2001', 'UASC': '1'},#Fail B
        {'CHILD': '106', 'DOB': '04/11/2004', 'UASC': '1'},#Fail B
        {'CHILD': '107', 'DOB': '23/07/2002', 'UASC': '1'},#Pass B
        {'CHILD': '108', 'DOB': '19/02/2003', 'UASC': '0'},#Fail C
        {'CHILD': '109', 'DOB': '14/06/2003', 'UASC': '0'},#Fail D
        {'CHILD': '110', 'DOB': '03/03/2002', 'UASC': '0'},
    ])"""

metadata_205 = """metadata_205 = {
        'collection_start': '01/04/2020',
        'collection_end': '31/03/2021',
    }"""

fake_dfs_205_xml = """fake_dfs_205_xml = {
        'UASC': fake_uasc_205,
        'UASC_last': fake_uasc_prev_205,
        'Header': fake_header_205,
        'Header_last': prev_fake_header_205,
        'metadata': {**metadata_205, **{'file_format': 'xml'}},
    }"""

fake_dfs_205_csv_1 = """fake_dfs_205_csv_1 = {
        'UASC': fake_uasc_205,
        'UASC_last': fake_uasc_prev_205,
        'Header': fake_header_205,
        'metadata': {**metadata_205, **{'file_format': 'csv'}},
    }"""

fake_dfs_205_csv_2 = """fake_dfs_205_csv_2 = {
        'UASC': fake_uasc_205,
        'UASC_last': fake_uasc_prev_205,
        'metadata': {**metadata_205, **{'file_format': 'csv'}},
    }"""


def handle_imports(validator_code_block):
    if "add_CLA_column" in validator_code_block:
        validator_code_block = (
            "from validator903.utils import add_col_to_tables_CONTINUOUSLY_LOOKED_AFTER as add_CLA_column  # Check 'Episodes' present before use!\n"
            + validator_code_block
        )
    if "merge_postcodes" in validator_code_block:
        validator_code_block = (
            "from validator903.datastore import merge_postcodes\n"
            + validator_code_block
        )
    if "ErrorDefinition" in validator_code_block:
        validator_code_block = (
            "from validator903.types import ErrorDefinition\n" + validator_code_block
        )
    if "IntegrityCheckDefinition" in validator_code_block:
        validator_code_block = (
            "from validator903.types import IntegrityCheckDefinition\n"
            + validator_code_block
        )
    if "MissingMetadataError" in validator_code_block:
        validator_code_block = (
            "from validator903.types import MissingMetadataError\n"
            + validator_code_block
        )
    if "pd." in validator_code_block:
        validator_code_block = "import pandas as pd\n\n" + validator_code_block

    return validator_code_block


def insert_code(si, code_block, test_data):
    return code_block[:si] + "\n    " + test_data + "\n" + code_block[si:]


def handle_test_data(code_block):
    si = code_block.index("):") + 2
    if "fake_dfs_205_csv_2" in code_block:
        code_block = insert_code(si, code_block, fake_dfs_205_csv_2)
    if "fake_dfs_205_csv_1" in code_block:
        code_block = insert_code(si, code_block, fake_dfs_205_csv_1)
    if "fake_dfs_205_xml" in code_block:
        code_block = insert_code(si, code_block, fake_dfs_205_xml)
    if "metadata_205" in code_block:
        code_block = insert_code(si, code_block, metadata_205)
    if "prev_fake_header_205" in code_block:
        code_block = insert_code(si, code_block, fake_prev_header_205)
    if "fake_header_205" in code_block:
        code_block = insert_code(si, code_block, fake_header_205)
    if "fake_uasc_prev_205" in code_block:
        code_block = insert_code(si, code_block, fake_uasc_prev_205)
    if "fake_uasc_205" in code_block:
        code_block = insert_code(si, code_block, fake_uasc_205)
    if "pd." in code_block:
        code_block = insert_code(si, code_block, "import pandas as pd")
    return code_block


def get_locations(delimeter, text):
    return [(i.start(), i.end(), i.groups()[0]) for i in re.finditer(delimeter, text)]


def run():
    with open("./validator903/validators.py") as validators_file:
        validators_text = validators_file.read()

    with open("./tests/test_validators.py") as validator_tests_file:
        tests_text = validator_tests_file.read()

    delimeter = r"def validate_([A-Za-z0-9]+)\(\):"
    test_delimeter = r"def test_validate_([A-Za-z0-9]+)\(\):"

    # Find the function definitions in both files, get their code
    function_locations = get_locations(delimeter, validators_text)
    test_locations = get_locations(test_delimeter, tests_text)

    # Loop over each function definition
    for idx, function in enumerate(function_locations):
        validator_title = function[2]

        # Get function text: This currently misses potential comments written before the function definitions
        if (idx + 1) < len(function_locations):
            validator_code_block = (
                "\n\n"
                + validators_text[function[0] : function_locations[idx + 1][0]]
                + "\n"
            )
        else:
            validator_code_block = "\n\n" + validators_text[function[0] :] + "\n"

        validator_code_block = handle_imports(validator_code_block).replace(
            "def validate_{}".format(validator_title), "def validate"
        )

        # Add tests: This currently misses potential comments written before the function definitions
        linked_tests = list(filter(lambda x: x[2] == validator_title, test_locations))
        for test in linked_tests:
            test_code_block = ""
            try:
                start_index = test[0]
                end_index = test[1] + tests_text[test[1] :].index("def ")
                test_code_block += tests_text[start_index:end_index]
            except ValueError as verr:
                # We've likely reached the end of the file
                test_code_block += tests_text[test[0] :]
            test_code_block = handle_test_data(test_code_block)
            test_code_block = test_code_block.replace(
                "def test_validate_{}".format(validator_title), "def test_validate"
            )

        # Make sure test is pointed at more generically-named function now
        test_code_block = re.sub(
            "\svalidate_[A-Za-z0-9]{0,4}\(", " validate(", test_code_block
        )

        # Format with black before saving it
        validator_code_block = (
            format_str(validator_code_block, mode=FileMode()) + "\n\n"
        )
        test_code_block = format_str(test_code_block, mode=FileMode())

        with open(
            "./validator903/validators/rule_{}.py".format(validator_title), "w"
        ) as validator_file:
            validator_file.write(validator_code_block)
            validator_file.write(test_code_block)


if __name__ == "__main__":
    run()
