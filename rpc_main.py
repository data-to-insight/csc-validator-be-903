import pandas as pd
from prpc_python import RpcApp

from lac_validator import lac_validator_class as lac_class
from lac_validator.ruleset import create_registry

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
def lac_validate(lac_data=None, selected_rules=None, ruleset="lac_2022_23"):
    """
    :param dict lac_data: keys are table names and values are LAC csv files.
    :param list selected_rules: array of rules the user has chosen. consists of rule codes as strings.
    :param ruleset: rule pack that should be run. lac_2022_23 is for the year 2022

    :return issue_report: issue locations in the data.
    :return rule_defs: rule codes and descriptions of the rules that triggers issues in the data.
    """
    # TODO put in processing so that a list of file references can be recieved and the names of the files are deduced from thier content.
    p4a_path = "tests\\fake_data\placed_for_adoption_errors.csv"
    ad1_path = "tests\\fake_data\\ad1.csv"

    # construct 'files' list of dicts (nb filetexts are bytes not str)
    # with open(p4a_path.name, 'rb') as f:
    #     p4a_filetext = f.read()

    # with open(ad1_path.name, 'rb') as f:
    #     ad1_filetext = f.read()

    with open(p4a_path, 'rb') as f:
        p4a_filetext = f.read()

    with open(ad1_path, 'rb') as f:
        ad1_filetext = f.read()


    # files_list = [
    #     dict(name=p4a_path.name, description='This year', fileText=p4a_filetext),
    #     dict(name=ad1_path.name, description='This year', fileText=ad1_filetext),
    # ]
    files_list = [
        dict(name=p4a_path, description='This year', fileText=p4a_filetext),
        dict(name=ad1_path, description='This year', fileText=ad1_filetext),
    ]

    # the rest of the metadata is added in read_from_text() when instantiating Validator
    metadata = {'collectionYear': '2022',
                'localAuthority': 'E09000027'}

    v = lac_class.LacValidationSession(metadata=metadata, files=files_list, ruleset=ruleset, selected_rules=selected_rules)
    results = v.ds_results
    r = Report(results)
    full_issue_df = lac_class.create_issue_df(r.report, r.error_report)

    # what the frontend will display
    issue_report = full_issue_df.to_json(orient="records")

    # what the user will download
    user_report = r.report.to_json(orient="records")

    # TODO should a dict be returned here so that variables can be accessed by name instead of index position?
    return issue_report, user_report

    