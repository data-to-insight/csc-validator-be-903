import datetime
import logging
import json
from prpc_python import RpcApp

from lac_validator import lac_validator_class as lac_class
from lac_validator.ruleset import create_registry
from lac_validator.utils import process_uploaded_files

from typing import Optional

from validator903.ingress import read_from_text
from validator903.report import Report


logger = logging.getLogger(__name__)
handler = logging.FileHandler(
    datetime.datetime.now().strftime("lac validator --%d-%m-%Y %H.%M.%S.log")
)

f_format = logging.Formatter("%(asctime)s - %(levelname)s - % (message)s")
handler.setFormatter(f_format)
logger.addHandler(handler)

app = RpcApp("validate_lac")
@app.call
def get_rules(ruleset:str="lac2022_23")->str:
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

    return json.dumps(rules)

@app.call
def generate_tables(lac_data:dict)->dict[str, dict]:

    """
    :param lac_data: files uploaded by user mapped to the field where files were uploaded.
    :return lac_data_tables:  a dictionary of dataframes that has been converted to json.
    """
    files_list = process_uploaded_files(lac_data)

    data_files, _ = read_from_text(files_list)

    # what the frontend will display
    lac_data_tables = {table_name:table_df.to_json(orient="records") for table_name, table_df in  data_files.items()}
    
    return lac_data_tables


@app.call
def lac_validate(lac_data:dict, file_metadata:dict,  selected_rules: Optional[list[str]]=None, ruleset:str="lac2022_23"):
    """
    :param lac_data: keys are table names and values are LAC csv files.
    :param file_metadata: contains collection year and local authority as strings.
    :param selected_rules: array of rules the user has chosen. consists of rule codes as strings.
    :param ruleset: rule pack that should be run. lac2022_23 will run the 2022/2023 validation rules.

    :return issue_report: issue locations in the data.
    :return rule_defs: rule codes and descriptions of the rules that triggers issues in the data.
    """
    # p4a_path = "tests\\fake_data\\placed_for_adoption_errors.csv"
    # ad1_path = "tests\\fake_data\\ad1.csv"
    # file_metadata = {"collectionYear": "2022", "localAuthority": "E09000027"}
    # lac_data = {"This year":[p4a_path, ad1_path], "Prev year": [p4a_path]}

    files_list = process_uploaded_files(lac_data)

    v = lac_class.LacValidator(metadata=file_metadata, files=files_list, ruleset=ruleset, selected_rules=selected_rules)
    results = v.ds_results
    r = Report(results)
    full_issue_df = lac_class.create_issue_df(r.report, r.error_report)

    # what the frontend will display
    issue_report = full_issue_df.to_json(orient="records")
    lac_data_tables = {table_name:table_df.to_json(orient="records") for table_name, table_df in  v.dfs.items()}
    
    # what the user will download
    user_reports = [r.report.to_json(orient="records"), r.error_report.to_json(orient="records"), r.error_summary.to_json(orient="records"),]

    # TODO check that user reports are downloaded with the appropriate names.
    validation_results = {"issue_locations": [issue_report], "data_tables":[lac_data_tables], "user_report":user_reports}
    return validation_results
