import importlib
from dataclasses import dataclass
from typing import Callable, Optional


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
    message: Optional[str]= None,
    affected_fields: Optional[list[str]]= None,

    @property
    def code_module(self):
        return importlib.import_module(self.func.__module__)
