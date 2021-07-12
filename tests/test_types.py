from validator903.types import ErrorDefinition

def test_errordefinition():
    error = ErrorDefinition(
        code='203',
        description='Test error',
        affected_fields=['SOME_FIELD'],
    )

    assert error.code == '203'
    assert error.description == 'Test error'
    assert error.affected_fields == ['SOME_FIELD']