from pathlib import Path

from lac_validator.rule_engine import RuleDefinition, YearConfig
from lac_validator.rules.lac2024_25 import registry as prev_registry
from lac_validator.rules.ruleset_utils import (
    extract_validator_functions,
    update_validator_functions,
)

files = Path(__file__).parent.glob("*.py")
this_year_validator_funcs: dict[str, RuleDefinition] = extract_validator_functions(
    files
)
# if any rules need to be deleted, add their codes as strings into del_list
del_list: list[str] = [

]
this_year_config = YearConfig(
    deleted=del_list, added_or_modified=this_year_validator_funcs
)

registry = update_validator_functions(prev_registry, this_year_config)
__all__ = ["registry"]
