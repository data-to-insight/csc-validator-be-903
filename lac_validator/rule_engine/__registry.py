from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional


@dataclass(frozen=True, eq=True)
class RuleDefinition:
    """
    A dataclass type class used in each validation to assign information about
    each validation rule to the rule.

    :param str code: The rule code for each rule.
    :param Callable func: logic of the validation rule function.
    :param str message: The message to be displayed if rule is flagged.
    :param str affected_fields: The fields/columns affected by a validation rule.

    :returns: RuleDefinition object containing information about validation rules.
    :rtype: dataclass object.
    """

    code: str
    func: Callable
    message: Optional[str] = None
    affected_fields: Optional[list[str]] = None
    tables: Optional[list[str]] = (None,)


def rule_definition(
    code: str,
    message: Optional[str] = None,
    affected_fields: Optional[list[str]] = None,
    tables: Optional[list[str]] = None,
):
    """
    Creates the rule definition for validation rules using RuleDefinition class as a template.

    :param str code: The rule code for each rule.
    :param str message: The message displayed for each validation rule.
    :param str affected_fields: The fields/columns affected by a validation rule.

    :returns: RuleDefinition object containing information about validation rules.
    :rtype: RuleDefiniton class object.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        definition = RuleDefinition(
            code=str(code),
            func=func,
            message=message,
            affected_fields=affected_fields,
            tables=tables,
        )
        # when validator funcs are created, give them a unique attribute that they can be
        # recognised by when the file is read later.
        wrapper.rule = definition
        return wrapper

    return decorator


@dataclass(eq=True)
class YearConfig:
    deleted: list[str]
    added_or_modified: dict[str, RuleDefinition]
