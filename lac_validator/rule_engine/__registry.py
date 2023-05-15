from functools import wraps
from typing import Callable, Iterable
from lac_validator.rule_engine.__api import RuleDefinition


class __Registry:
    """Contains information about all validation rules including definition and issue error locations. Allows iterating through validation rules."""

    def __init__(self):
        """
        Initialises an empty dicitonary to be filled with validation rules and their
        RuleDefinitions.
        """

        self._registry = {}

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

    def add_ruleset(self, ruleset_dict):
        """
        to merge two rulesets, registry might be converted into a dict.
        this method brings dicts back into registry format so that they can be run on user data.

        :param dict ruleset_dict: keys are rule codes and values are rule definition objects.
        """
        self._registry = ruleset_dict

    def get(self, code: int):
        """
        Extracts code for each validation rule.

        :param int code: The code for a validation rule.
        :returns: Rule code for validation rule.
        :rtype: int
        """

        return self._registry.get(code)

    def __getitem__(self, code: int):
        """
        Used to return individual rules by code to allow iterating.

        :param int code: The code for a particular validation rule.
        :returns: A RuleDefinition for a particular validation rule, by rule code.
        :rtype: RuleDefinition object.
        """

        return self._registry[code]

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

    def reset(self):
        """
        delete all rules imported into registry.
        """
        self._registry = {}


registry = __Registry()


def rule_definition(
    code: int,
    message: str = None,
    affected_fields: Iterable[str] = None,
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
        registry.add(definition)
        wrapper.__rule_def__ = definition
        return wrapper

    return decorator
