import importlib
from lac_validator.rule_engine import RuleDefinition
from typing import Iterable

def extract_validator_functions(file_paths:Iterable, marker:str="rule") -> dict[str, RuleDefinition]:
    """
    :param list file_paths: list of file paths to extract functions from.
    :param str marker: marker to identify functions to extract.

    :return: functions extracted from files.
    :rtype: dict
    """
    validator_funcs: dict[str, RuleDefinition] = {}
    for path in file_paths:
        if path.stem == "__init__":
            continue
        rule_content = importlib.import_module(f"lac_validator.rules.{path.parent.stem}.{path.stem}")
        validator_func = {element.rule.code:element.rule for _, element in vars(rule_content).items() if hasattr(element, marker)}
        duplicate_funcs = set(validator_func.keys()) & set(validator_funcs.keys())
        if duplicate_funcs:
            raise ValueError(f"Rule with code {duplicate_funcs} already exists")
        validator_funcs.update(validator_func)
    return validator_funcs

def update_validator_functions(prev_registry, this_year_config:dict) -> dict:
    """
    :param dict prev_registry: previous year's registry.
    :param dict this_year_config: codes of rules that have been added or deleted.

    :return: valid validator functions according to config.
    :rtype: dict
    """
    prev_validator_funcs = prev_registry
    # Rules present in both will be updated to this year's version. rules present in only this year will be added.
    updated_validator_funcs = prev_validator_funcs | this_year_config["added_or_modified"]
    # delete rules by their rules codes, if specified.
    for deleted_rule in this_year_config["deleted"]:
        del updated_validator_funcs[deleted_rule]
    return updated_validator_funcs 