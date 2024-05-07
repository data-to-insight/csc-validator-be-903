"""Tests for all configured errors"""

import pandas as pd
import pytest

from lac_validator.datastore import copy_datastore
from lac_validator.rule_engine import RuleDefinition
from lac_validator.rules.lac2022_23 import registry
from lac_validator.types import MissingMetadataError


def test_all_configured_error_definitions():
    codes = []
    for rule_code, rule in registry.items():
        assert isinstance(
            rule, RuleDefinition
        ), f"The returned rule is not of RuleDefinition type ({rule})"

        # Check types of the fields
        assert isinstance(
            rule.code, str
        ), f"The error code {rule.code} is not a string!"
        assert isinstance(
            rule.message, str
        ), f"The error description {rule.message} is not a string!"
        assert isinstance(
            rule.affected_fields, list
        ), f"The affected fields {rule.affected_fields} is not a list!"
        assert all(
            isinstance(f, str) for f in rule.affected_fields
        ), f"Not all fields in affected_fields are strings!"

        assert rule.code not in codes, f"Error code {rule.code} is duplicated!"
        codes.append(rule.code)


@pytest.mark.parametrize(
    "data_choice",
    [
        pytest.param("dummy_empty_input", id="empty input with columns"),
        pytest.param("dummy_input_data", id="input with fake csvs"),
        pytest.param("{}", id="totally empty input"),
    ],
)
def test_all_configured_error_functions(
    data_choice, dummy_empty_input, dummy_input_data
):
    dummy_data = eval(data_choice)
    for rule_code, rule in registry.items():
        dummy_data_copy = copy_datastore(dummy_data)
        try:
            result = rule.func(dummy_data_copy)
        except MissingMetadataError:
            result = {}

        for table_name, issue_list in result.items():
            assert (
                table_name in dummy_data_copy
            ), f"Returned error table name {table_name} not recognized!"
            assert isinstance(
                issue_list, list
            ), f"Returned list of error locations {issue_list} is not a list (its a {type(issue_list)})!"
            for issue_location in issue_list:
                assert (
                    issue_location in dummy_data_copy[table_name].index
                ), f"Location {issue_location} not found in {table_name} index - check returned locations!"


def test_has_correct_table_names(dummy_input_data):
    for rule_code, rule in registry.items():
        dummy_input_data_copy = copy_datastore(dummy_input_data)

        # lazy engineer's no-change workaround - if Header's 'UASC' column or metadata's 'provider_info' is missing,
        # it results in this test failing as some checks then return empty dict {} to signal they were skipped
        dummy_input_data_copy["Header"].loc[:, "UASC"] = "0"
        dummy_provider_info = pd.DataFrame(
            columns=[
                "URN",
                "LA_NAME_FROM_FILE",
                "PLACE_CODES",
                "PROVIDER_CODES",
                "REG_END",
                "POSTCODE",
                "LA_NAME_INFERRED",
                "LA_CODE_INFERRED",
            ],
            index=[0, 1, 2, 3, 4, 5],
            data="nonsense",
        )
        dummy_input_data_copy["metadata"].update({"provider_info": dummy_provider_info})

        result = rule.func(dummy_input_data_copy)

        errors_skipped_for_csv = ("105",)
        if rule.code.lower() not in errors_skipped_for_csv:
            assert (
                len(result) > 0
            ), f"Validator for {rule.code} does not appear to operate on any configured table names - check spelling!"
        assert all(
            r in dummy_input_data_copy for r in result
        ), f"Validator for {rule.code} returns a wrong table name!"
