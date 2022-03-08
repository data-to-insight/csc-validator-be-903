"""Tests for all configured errors"""
import pytest
from validator903.config import configured_errors, column_names
import pandas as pd
from validator903.types import ErrorDefinition, MissingMetadataError
from validator903.datastore import copy_datastore

def test_all_configured_error_definitions():
    codes = []
    for error, _ in configured_errors:
        # Check that all errors are ErrorDefinition
        assert isinstance(error, ErrorDefinition), f'The returned error is not an ErrorDefinition ({error})'

        # Check types of the fields
        assert isinstance(error.code, str), f'The error code {error.code} is not a string!'
        assert isinstance(error.description, str), f'The error description {error.description} is not a string!'
        assert isinstance(error.affected_fields, list), f'The affected fields {error.affected_fields} is not a list!'
        assert all(isinstance(f, str) for f in error.affected_fields), f'Not all fields in affected_fields are strings!'
        
        assert error.code not in codes, f'Error code {error.code} is duplicated!'
        codes.append(error.code)

@pytest.mark.parametrize("data_choice", [
    pytest.param('dummy_empty_input', id='empty input with columns'),
    pytest.param('dummy_input_data', id='input with fake csvs'),
    pytest.param('{}', id='totally empty input'),
])
def test_all_configured_error_functions(data_choice, dummy_empty_input, dummy_input_data):
    dummy_data = eval(data_choice)
    for error_code, error_func in configured_errors:
        dummy_data_copy = copy_datastore(dummy_data)
        try:
            result = error_func(dummy_data_copy)
        except MissingMetadataError:
            result = {}

        for table_name, error_list in result.items():
            assert table_name in dummy_data_copy, f'Returned error table name {table_name} not recognized!'
            assert isinstance(error_list, list), f'Returned list of error locations {error_list} is not a list (its a {type(error_list)})!'
            for error_location in error_list:
                assert error_location in dummy_data_copy[table_name].index, f'Location {error_location} not found in {table_name} index - check returned locations!'


def test_has_correct_table_names(dummy_input_data):
    for error_def, error_func in configured_errors:
        dummy_input_data_copy = copy_datastore(dummy_input_data)

        # lazy engineer's no-change workaround - if Header's 'UASC' column or metadata's 'provider_info' is missing,
        # it results in this test failing as some checks then return empty dict {} to signal they were skipped
        dummy_input_data_copy['Header'].loc[:, 'UASC'] = '0'
        dummy_provider_info = pd.DataFrame(
            columns=['URN', 'LA_NAME_FROM_FILE', 'PLACE_CODES', 'PROVIDER_CODES',
                     'REG_END', 'POSTCODE', 'LA_NAME_INFERRED', 'LA_CODE_INFERRED'],
            index=[0, 1, 2, 3, 4, 5],
            data='nonsense'
        )
        dummy_input_data_copy['metadata'].update({'provider_info': dummy_provider_info})

        result = error_func(dummy_input_data_copy)

        errors_skipped_for_csv = ('105', )
        if error_def.code.lower() not in errors_skipped_for_csv:
            assert len(result) > 0, f'Validator for {error_def} does not appear to operate on any configured table names - check spelling!'
        assert all(r in dummy_input_data_copy for r in result), f'Validator for {error_def} returns a wrong table name!'

