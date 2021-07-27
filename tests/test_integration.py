"""Tests for all configured errors"""
from validator903.config import configured_errors
from validator903.types import ErrorDefinition

def test_all_configured_errors_are_unique():
    codes = []
    for error, error_func in configured_errors:
        # Check that all errors are ErrorDefinition
        assert isinstance(error, ErrorDefinition), f'The returned error is not an ErrorDefinition ({error})'

        # Check types of the fields
        assert isinstance(error.code, str), f'The error code {error.code} is not a string!'
        assert isinstance(error.description, str), f'The error description {error.description} is not a string!'
        assert isinstance(error.affected_fields, list), f'The affected fields {error.affected_fields} is not a list!'
        assert all(isinstance(f, str) for f in error.affected_fields), f'Not all fields in affected_fields are strings!'
        
        assert error.code not in codes, f'Error code {error.code} is duplicated!'
        codes.append(error.code)

