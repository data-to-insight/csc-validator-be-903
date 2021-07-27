import pytest
import os
import pandas as pd
from validator903.config import column_names 

@pytest.fixture
def dummy_input_data():
    file_path = os.path.join(os.path.dirname(__file__), 'fake_data')
    file_maps = {
        'header.csv': 'Header',
        'episodes.csv': 'Episodes',
    }

    out = {}
    for file, identifier in file_maps.items():
        path = os.path.join(file_path, file)
        df = pd.read_csv(path)
        out[identifier] = df

    return out

@pytest.fixture
def dummy_empty_input():
    return {
        table_name: pd.DataFrame(columns=c)
        for table_name, c in column_names.items()
    }
