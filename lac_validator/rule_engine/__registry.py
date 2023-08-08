from functools import wraps
from typing import Callable, Optional
from dataclasses import dataclass


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
    message: Optional[str]= None
    affected_fields: Optional[list[str]]= None


class Registry:
    """Contains information about all validation rules including definition and issue error locations. Allows iterating through validation rules."""

    def __init__(self, validator_funcs: dict[str, RuleDefinition]):
        """
        Wraps dict so that iteration is done over dict values instead of its keys.
        """
        self._registry = validator_funcs

    def __len__(self):
        """
        Provides the number of validation rules.

        :returns: The length number of rules in the registry.
        :rtype: int.
        """

        return len(self._registry)

    def __iter__(self):
        """
        Allows iterating through validation rules by code.

        :returns: Iterable of validation rules.
        :rtype: Iterable.
        """

        return iter(self._registry.values())

    def to_dict(self):
        """
        return: registry as a dict to enable full dictionary operations.
        rtype: dict
        """

        return self._registry


def rule_definition(
    code: str,
    message: Optional[str] = None,
    affected_fields: Optional[list[str]] = None,
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
            code=code,
            func=func,
            message=message,
            affected_fields=affected_fields,
        )
        # when validator funcs are created, give them a unique attribute that they can be 
        # recognised by when the file is read later.
        wrapper.rule = definition
        return wrapper

    return decorator
