import pandas as pd
from .types import ErrorDefinition

def fake_error():
    error = ErrorDefinition(
        code='1003',
        description='A fake error that fires if the child was born prior to 2006',
        affected_fields=['DOB'],
    )

    def _validate(dfs):
        if 'Header' not in dfs:
            return {}
        else:
            header = dfs['Header']
            mask = pd.to_datetime(header['DOB'], format='%d/%m/%Y', errors='coerce').dt.year <= 2006
            return {'Header': header.index[mask].tolist()}
    
    return error, _validate

def fake_error2():
    error = ErrorDefinition(
        code='2020',
        description='A fake error that fires if the child has a postcode containing F.',
        affected_fields=['HOME_POST'],
    )

    def _validate(dfs):
        if 'Episodes' not in dfs:
            return {}
        else:
            episodes = dfs['Episodes']
            mask = episodes['HOME_POST'].str.contains('F')
            return {'Episodes': episodes.index[mask].tolist()}

    return error, _validate