import importlib
from pathlib import Path
from lac_validator.rule_engine import Registry
from lac_validator.rule_engine import RuleDefinition

files = [p.stem for p in Path(__file__).parent.glob("*.py") if p.stem != "__init__"]

this_year_validator_funcs: dict[str, RuleDefinition] = {}
for rule_file in files:
    # get all the elements (functions, classes, variables) of the file and their attributes.
    rule_content = importlib.import_module(f"lac_validator.rules.lac2022_23.{rule_file}")
    rule_elements = {n:getattr(rule_content, n) for n in dir(rule_content)}
    # all validator functions have a decorator which attaches a "rule" attribute to them.
    validator_func = {element.rule.code: element.rule for _, element in rule_elements.items() if hasattr(element, "rule")}
    for rule_code in validator_func.keys():
        if rule_code in this_year_validator_funcs.keys():
            raise ValueError(f"Rule with code {rule_code} already exists")
    this_year_validator_funcs.update(validator_func)

registry = Registry(this_year_validator_funcs)

__all__=["registry"]