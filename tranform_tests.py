from os import listdir
from os.path import isfile, join

dirpath ="lac_validator\\rules\lac_2022_23"
onlyfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]
onlyfiles.remove("__init__.py")  

for rule_file in onlyfiles:
    # Read file contents.
    with open(join(dirpath,rule_file), "r") as f:
        rule_content = f.read()

    rule_content = rule_content.replace("error_defn, error_func = validate()", "")
    rule_content = rule_content.replace("error_func(fake_dfs)", "validate(fake_dfs)")

    # write new content to files.
    with open(f".\lac_validator\\rules\lac_2022_23\{rule_file}", "w") as rule_file:
        rule_file.write(rule_content)
    

