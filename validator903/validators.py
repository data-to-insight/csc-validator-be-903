import pandas as pd
from .types import ErrorDefinition

def fake_error(dfs):
    error = ErrorDefinition(
        code='1003',
        description='A fake error that fires if the child was born prior to 2006',
        affected_fields=['DOB'],
    )

    header = dfs['Header']
    mask = pd.to_datetime(header['DOB'], format='%d/%m/%Y').dt.year <= 2006
    
    return error, {'Header': header.index[mask].values}

def fake_error2(dfs):
    error = ErrorDefinition(
        code='2020',
        description='A fake error that fires if the child has a postcode containing F.',
        affected_fields=['HOME_POST'],
    )

    df = dfs['Episodes']
    mask = df['HOME_POST'].str.contains('F')
    
    return error, {'Episodes': df.index[mask].values}