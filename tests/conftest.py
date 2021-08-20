import pytest
import os
import pandas as pd
from validator903.config import column_names 

@pytest.fixture
def dummy_input_files():
    return  {
        'header.csv': 'Header',
        'episodes.csv': 'Episodes',
        'ad1.csv': 'AD1',
        'oc2.csv': 'OC2',
        'oc3.csv': 'OC3',
        'placed_for_adoption.csv': 'PlacedAdoption',
        'reviews.csv': 'Reviews',
        'uasc.csv': 'UASC',
    }

@pytest.fixture
def dummy_input_data(dummy_input_files):
    file_path = os.path.join(os.path.dirname(__file__), 'fake_data')

    out = {}
    for file, identifier in dummy_input_files.items():
        path = os.path.join(file_path, file)
        df = pd.read_csv(path)
        out[identifier] = df
    out['metadata'] = {}

    return out

@pytest.fixture
def dummy_postcodes():
    file_path = os.path.join(os.path.dirname(__file__), 'fake_data', 'postcodes_short.csv')
    return pd.read_csv(file_path)

@pytest.fixture
def dummy_empty_input():
    out = {
        table_name: pd.DataFrame(columns=c)
        for table_name, c in column_names.items()
    }
    out['metadata'] = {}
    return out
