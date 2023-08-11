# The code in this file adjusts the test functions to fit the revised structure of the validate functions.
# This is because the new validate function returns only the function object without the rule definition object.
# This is part of reshaping the rules.

import json

with open("files_failed.json", "r") as f:
    failed_paths = json.load(f)

# These are the variations of how the test functions ran their validate function. each had to be replaced accordingly.
# result = error_func(test_dfs)
# error_func(fake_dfs_partial)
# error_func(

for rule_file in failed_paths:
    # Read file contents.
    with open(rule_file, "r") as f:
        rule_content = f.read()

    rule_content = rule_content.replace("error_defn, error_func = validate()", "")
    rule_content = rule_content.replace("error_func(fake_dfs)", "validate(fake_dfs)")
    rule_content = rule_content.replace("error_func(", "validate(")
    rule_content = rule_content

    # write new content to files.
    with open(f"{rule_file}", "w") as rule_file:
        rule_file.write(rule_content)
