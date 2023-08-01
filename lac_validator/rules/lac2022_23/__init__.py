import importlib
from pathlib import Path

# TODO build out how this init file should look like next year. 
# the init files of each next year should import the rule package of the previous year
# and return a new registry that reflects the rule revisions of that year. e.g take rules A, B as-is, modify rule C and ignore/delete/do-not-run rule D, and take rule E as-is
# So the __init__.py file of lac202_23 should import the 

files = [p.stem for p in Path(__file__).parent.glob("*.py") if p.stem != "__init__"]

# TODO registry should be of Registry type (class in lac_validator\rule_engine\__registry.py)
registry = []
for rule_file in files:
    # get all the elements (functions, classes, variables) of the file and their attributes.
    rule_content = importlib.import_module(f"lac_validator.rules.lac2022_23.{rule_file}")
    rule_elements = {n:getattr(rule_content, n) for n in dir(rule_content)}
    # all validator functions have a decorator which attaches a "rule" attribute to them.
    validator_funcs = [v.rule for k, v in rule_elements.items() if hasattr(v, "rule")]
    # TODO reevaluate if validator_funcs should be a list or a dict, considering how easy it will be to compare rules present/absent/modified across years
    registry.extend(validator_funcs)

__all__=["registry"]