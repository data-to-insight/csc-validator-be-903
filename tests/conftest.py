import pytest
import os
import pandas as pd
from validator903.config import column_names 
from validator903.datastore import create_datastore


@pytest.fixture(scope="session")
def dummy_input_files():
    return  {
        'header.csv': 'Header',
        'episodes.csv': 'Episodes',
        'reviews.csv': 'Reviews',
        'uasc.csv': 'UASC',
        'oc2.csv': 'OC2',
        'oc3.csv': 'OC3',
        'ad1.csv': 'AD1',
        'placed_for_adoption.csv': 'PlacedAdoption',
        'previous_permanence.csv': 'PrevPerm',
        'missing.csv': 'Missing',
    }


@pytest.fixture(scope="session")
def dummy_metadata():
    return {
        'collectionYear': '2019/20',
        'localAuthority': 'test_LA',
    }


@pytest.fixture(scope="session")
def dummy_input_data(dummy_input_files, dummy_metadata):
    file_path = os.path.join(os.path.dirname(__file__), 'fake_data')

    out = {}
    for file, identifier in dummy_input_files.items():
        path = os.path.join(file_path, file)
        df = pd.read_csv(path)
        out[identifier] = df
        out[identifier + '_last'] = df.copy()

    return create_datastore(out, dummy_metadata)


@pytest.fixture(scope="session")
def dummy_empty_input(dummy_metadata):
    out = {
        table_name: pd.DataFrame(columns=c)
        for table_name, c in column_names.items()
    }
    out_last = {
        table_name + '_last': pd.DataFrame(columns=c)
        for table_name, c in column_names.items()
    }
    return create_datastore({**out, **out_last}, dummy_metadata)
