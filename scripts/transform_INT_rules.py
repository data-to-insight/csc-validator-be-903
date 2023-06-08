# The code in this file does the appropriate modifications on the INT files to put them in the new rule format.
# INT files were exceptions to most of the formats expected by the scripts that updated the rest of the rules.

import os


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def process_file(source_file, destination_file):
    with open(source_file, "r") as source:
        content = source.read()
        content = content.replace("fake_INT_file", "fake_INT_file.copy()")
        content = content.replace("fake_INT_header", "fake_INT_header.copy()")

        content = content.replace(
            "from validator903.types import IntegrityCheckDefinition",
            "from lac_validator.rule_engine import rule_definition\nfrom lac_validator.fixtures import fake_INT_header, fake_INT_file",
        )

        code = find_between(content, "code=", ",")
        message = find_between(content, "description=", ",")
        affected_fields = find_between(content, "affected_fields=", "],") + "]"

        start = content.index("error = IntegrityCheckDefinition(")

        end = content.index("def _validate(dfs)")
        content = content.replace(content[start : end + len("def _validate(dfs):")], "")
        content = content.replace(
            "def validate():",
            f"@rule_definition(\ncode={code},\nmessage={message},\naffected_fields={affected_fields},\n)\ndef validate(dfs):",
        )
        cleaned_code = code.replace('"', "")
        content = content.replace("return error, _validate", "")
        content = content.replace(
            f"erro_defn, error_func = validate_{cleaned_code}()\n", ""
        )
        content = content.replace("error_func", "validate")

    with open(destination_file, "w") as destination:
        destination.write(content)


def main():
    source_directory = os.path.join("validator903", "validators")
    destination_directory = os.path.join("lac_validator", "rules", "lac2022_23")

    # Iterate over files in the source directory
    for filename in os.listdir(source_directory):
        if filename.endswith(".py") and "INT" in filename:
            source_file = os.path.join(source_directory, filename)
            destination_file = os.path.join(destination_directory, filename)
            process_file(source_file, destination_file)

    print("Files copied and modified successfully!")


if __name__ == "__main__":
    main()
