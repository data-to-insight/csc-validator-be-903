# The code in this file transformed the former rule structure into the new one that uses generators.
# It was implemented and run immediately after split.py as the second step of the tool rewrite.
# The other scripts were run to cover exceptions that weren't captured by this one.

from os import listdir
from os.path import isfile, join

dirpath ="validator903\\validators"
onlyfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]
# onlyfiles.remove("__init__.py")

def update_imports(imprts):
    
    imprts = imprts + "\nimport pandas as pd"
    if "from validator903.types import ErrorDefinition" in imprts:
        imprts = imprts.replace("from validator903.types import ErrorDefinition", "from lac_validator.rule_engine import rule_definition")
    else:
        imprts = imprts + "\nfrom lac_validator.rule_engine import rule_definition"
    return imprts

def transform_rule(rule_file_name):
    # Read file contents.
    with open(join(dirpath,rule_file_name), "r") as f:
        rule_content = f.read()

    test_validate_start = rule_content.find("def test_validate()")
    test_validate = rule_content[test_validate_start: ]

    validate_start = rule_content.find("def validate()")
    validate = rule_content[validate_start: test_validate_start]
    subvalidate_end = validate.rfind("return") # finds the outer last return statement such that it can be excluded.

    subvalidate_start = validate.find("def _validate(dfs)")
    subvalidate = validate[subvalidate_start: subvalidate_end].replace("_validate", "validate")

    rule_def_start = validate.find("error = ErrorDefinition")
    rule_def = validate[rule_def_start:subvalidate_start]
    rule_def = rule_def.replace("error = ErrorDefinition", "@rule_definition").replace("description", "message").strip()

    imprts = rule_content[:validate_start]
    imprts_updated = update_imports(imprts)
    # write new content to files.
    with open(f".\lac_validator\\rules\lac2022_23\{rule_file_name}", "w") as rule_file:
        rule_file.write(f"{imprts_updated}\n{rule_def}\n{subvalidate}\n{test_validate}")

for rule_file in onlyfiles:
    transform_rule(rule_file)

