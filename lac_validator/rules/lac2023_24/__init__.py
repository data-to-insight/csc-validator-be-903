from lac_validator.rules.lac2022_23 import registry as prev_registry
import importlib
from pathlib import Path
from lac_validator.rule_engine import Registry
from lac_validator.rule_engine import RuleDefinition

files = [p.stem for p in Path(__file__).parent.glob("*.py") if p.stem != "__init__"]

# validator_funcs = create_validator_funcs(files)
ruleset_year = "lac2023_24"
this_year_validator_funcs: dict[str, RuleDefinition] = {}
for rule_file in files:
    # get all the elements (functions, classes, variables) of the file and their attributes.
    rule_content = importlib.import_module(f"lac_validator.rules.{ruleset_year}.{rule_file}")
    rule_elements = {n:getattr(rule_content, n) for n in dir(rule_content)}
    # all validator functions have a decorator which attaches a "rule" attribute to them.
    validator_func = {element.rule.code:element.rule for _, element in rule_elements.items() if hasattr(element, "rule")}
    this_year_validator_funcs.update(validator_func)
registry = Registry(this_year_validator_funcs)

### temporary demo code to delete rules that are not valid for this year.
del_list = ['1000', '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '101', '1010', '1011', '1012', '1014', '1015', '102', '103', '104', '105', '112', '113', '114', '115',]
this_year_config = {"deleted": del_list, "added": this_year_validator_funcs}

# registry = update_registry(prev_registry, this_year_config)
prev_validator_funcs = prev_registry.to_dict()

# Rules present in both will be updated to this year's version. rules present in only this year will be added.
complete_validator_funcs = prev_validator_funcs | this_year_config["added"]
# delete specified rules as specified by their rules codes.
for deleted_rule in this_year_config["deleted"]:
    del complete_validator_funcs[deleted_rule]

# registry = Registry(complete_validator_funcs)
registry = complete_validator_funcs