"""Tests for all configured errors"""
from validator903.config import configured_errors, column_names
import pandas as pd
from validator903.types import ErrorDefinition

def create_dummy_data():
    return {
        table_name: pd.DataFrame(columns=c)
        for table_name, c in column_names.items()
    }

def test_all_configured_errors():
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

def test_all_configured_error_functions():
    # First things first - we pull in some dummy data
    dummy_data = create_dummy_data()
    for error_code, error_func in configured_errors:
        result = error_func(dummy_data)

        for table_name, error_list in result.items():
            assert table_name in dummy_data, f'Returned error table name {table_name} not recognized!'
            assert isinstance(error_list, list), f'Returned list of error locations {error_list} is not a list (its a {type(error_list)})!'
            for error_location in error_list:
                assert error_location in dummy_data[table_name].index, f'Location {error_location} not found in {table_name} index - check returned locations!'


