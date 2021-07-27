import pandas as pd
from .types import ErrorDefinition

def fake_error():
    error = ErrorDefinition(
        code='1003',
        description='A fake error that fires if the child was born prior to 2006',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        header = dfs['Header']
        mask = pd.to_datetime(header['DOB'], format='%d/%m/%Y').dt.year <= 2006
        return {'Header': header.index[mask].tolist()}
    
    return error, _validate

def fake_error2():
    error = ErrorDefinition(
        code='2020',
        description='A fake error that fires if the child has a postcode containing F.',
        affected_fields=['HOME_POST'],
    )

    def _validate(dfs):
        df = dfs['Episodes']
        mask = df['HOME_POST'].str.contains('F')
        return {'Episodes': df.index[mask].tolist()}

    return error, _validate