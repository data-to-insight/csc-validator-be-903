from functools import wraps
from typing import Callable, Optional
import importlib
from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class RuleDefinition:
    """
    A dataclass type class used in each validation to assign information about
    each validation rule to the rule.

    :param int code: The rule code for each rule.
    :param function func: Used to import the validation rule function.
    :param str message: The message to be displayed if rule is flagged.
    :param str affected_fields: The fields/columns affected by a validation rule.

    :returns: RuleDefinition object containing information about validation rules.
    :rtype: dataclass object.
    """

    code: str
    func: Callable
    message: Optional[str]= None
    affected_fields: Optional[list[str]]= None
    @property
    def code_module(self):
        # TODO check if this line is still necessary after recent changes to registry.
        return importlib.import_module(self.func.__module__)


class Registry:
    """Contains information about all validation rules including definition and issue error locations. Allows iterating through validation rules."""

    def __init__(self, validator_funcs: dict[str, RuleDefinition]):
        """
        converts list of validator functions into a dictionary of rule definitions.
        """
        self._registry = validator_funcs
        
    def add(self, rd: RuleDefinition):
        """
        Adds rules to the registry for iterating through and validating.

        :param RuleDefinition-object: Object containing rule definition for every validation rule.
        :returns: Adds rule definition fo rule to registry. Error if the rule code already exists.
        :rtype: RuleDefinition object dictionary entry.
        """

        if str(rd.code) in self._registry:
            # prevent duplicate rules from being created
            raise ValueError(f"Rule with code {rd.code} already exists")
        self._registry[str(rd.code)] = rd

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
        return: list of rule codes present in registry.
        """

        return self._registry


def rule_definition(
    code: str,
    message: Optional[str] = None,
    affected_fields: Optional[list[str]] = None,
):
    """
    Creates the rule definition for validation rules using RuleDefinition class as a template.

    :param int code: The rule code for each rule.
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
