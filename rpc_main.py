import pandas as pd
from prpc_python import RpcApp

from lac_validator import lac_validator_class as lac_class
from lac_validator.ruleset import create_registry

from validator903.ingress import read_from_text
from validator903.report import Report

app = RpcApp("validate_lac")

@app.call
def get_rules(ruleset="lac_2022_23"):
    """
    :param str ruleset: validation ruleset according to year published.
    :return rules_df: available rule codes and definitions according to chosen ruleset.
    """

    registry = create_registry(ruleset)
    rules = []
    for rule in registry:
        rules.append(
            {
                "code": str(rule.code),
                "description": str(rule.code) + " - " + str(rule.message),
            }
        )

    # dataframe of rule_definitions
    rules_df = pd.DataFrame(rules)

    json_rules_df = rules_df.to_json(orient="records")
    return json_rules_df

@app.call
def generate_tables(lac_data):
    # TODO if user uploads tabular data, return as-is. if xml, convert to csv.
    """
    :param lac_data: file reference to a LAC file(s) uploaded by user.
    :return json_data_files:  a dictionary of dataframes that has been converted to json.
    """

    files_list = [
        dict(name=lac_data.filename, description='This year', fileText=lac_data.read()),
    ]

    data_files, _ = read_from_text(files_list)

    # what the frontend will display
    json_data_files = {table_name:table_df.to_json(orient="records") for table_name, table_df in  data_files.items()}
    
    return json_data_files


@app.call
def lac_validate(lac_data, file_metadata,  selected_rules=None, ruleset="lac_2022_23"):
    """
    :param dict lac_data: keys are table names and values are LAC csv files.
    :param  dict file_metadata: contains collection year and local authority as strings.
    :param list selected_rules: array of rules the user has chosen. consists of rule codes as strings.
    :param ruleset: rule pack that should be run. lac_2022_23 is for the year 2022

    :return issue_report: issue locations in the data.
    :return rule_defs: rule codes and descriptions of the rules that triggers issues in the data.
    """
    # TODO put in processing so that a list of file references can be recieved and the names of the files are deduced from thier content.
    # p4a_path = "tests\\fake_data\\placed_for_adoption_errors.csv"
    # ad1_path = "tests\\fake_data\\ad1.csv"

    files_list = [
        dict(name=lac_data.filename, description='This year', fileText=lac_data.read()),
    ]

    v = lac_class.LacValidationSession(metadata=file_metadata, files=files_list, ruleset=ruleset, selected_rules=selected_rules)
    results = v.ds_results
    r = Report(results)
    full_issue_df = lac_class.create_issue_df(r.report, r.error_report)

    # what the frontend will display
    issue_report = full_issue_df.to_json(orient="records")
    json_data_files = {table_name:table_df.to_json(orient="records") for table_name, table_df in  v.dfs.items()}
    placeholder_var = pd.DataFrame().to_json(orient="records")
    
    # what the user will download
    user_report = r.report.to_json(orient="records")

    # TODO should a dict be returned here so that variables can be accessed by name instead of index position?
    return issue_report, placeholder_var, json_data_files, user_report

    