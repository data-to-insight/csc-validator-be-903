from os import listdir
from os.path import isfile, join

dirpath ="validator903\\validators"
onlyfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]
onlyfiles.remove("__init__.py")

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
    subvalidate = validate[subvalidate_start: subvalidate_end].replace("_", "")

    rule_def_start = validate.find("error = ErrorDefinition")
    rule_def = validate[rule_def_start:subvalidate_start]
    rule_def = rule_def.replace("error = ErrorDefinition", "@rule_definition").replace("description", "message").strip()

    imports = rule_content[:validate_start]
    def de_tab(line):
        if line[:8].isspace():
            return line[8:]
        else: 
            return line
            something

    # write new content to files.
    with open(f".\lac_validator\\rules\lac_2022_23\{rule_file_name}", "w") as rule_file:
        rule_file.write(f"{imports}\n{rule_def}\n{subvalidate}\n{test_validate}")

for rule_file in onlyfiles:
    transform_rule(rule_file)

