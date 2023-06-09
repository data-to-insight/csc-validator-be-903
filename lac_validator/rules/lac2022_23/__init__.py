import importlib
from pathlib import Path

files = [p.stem for p in Path(__file__).parent.glob("*.py") if p.stem != "__init__"]

registry = []
for rule_file in files:
    # get all the elements (functions, classes, variables) of the file and their attributes.
    rule_content = importlib.import_module(f"lac_validator.rules.lac2022_23.{rule_file}")
    rule_elements = {n:getattr(rule_content, n) for n in dir(rule_content)}
    # all validator functions have a decorator which attaches a "rule" attribute to them.
    validator_funcs = [v.rule for k, v in rule_elements.items() if hasattr(v, "rule")]
    registry.extend(validator_funcs)

__all__=["registry"]