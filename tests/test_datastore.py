import numpy as np
import pandas as pd
import pytest
from qlacref_postcodes import Postcodes
from validator903.datastore import create_datastore, _add_postcode_derived_fields, merge_postcodes


def test_postcode_key():
    """
    This is a bit of an odd test, but if this fails, then there isn't a valid postcode key in .qlacref - if that's
    the case then, either the postcode code is broken or someone's tampered with the key.

    If that's the case, please check your version of the 'quality-lac-data-ref-postcodes' and the key in
    .qlacref/id_rsa.pub and make sure everything is set up correctly. To run this project more securely, please
    provide the environment variable 'QLACREF_PC_KEY' with a verified public key for the postcode data.
    """
    pc = Postcodes()
    pc.load_postcodes('A')
    assert pc.dataframe.shape[0] > 10000


def test_create_datastore(dummy_input_data):
    metadata = {
        'collectionYear': '2019/20',
        'localAuthority': 'test_LA'
    }
    ds = create_datastore(dummy_input_data, metadata)

    assert ds['metadata'] == metadata


def test_add_postcodes():
    df = pd.DataFrame([['AB30 1GX', 'AB30 1ZJ']], columns=["HOME_POST", "PL_POST"])
    _add_postcode_derived_fields(df, '')
    assert df.PL_DISTANCE[0] == 0.8


@pytest.mark.parametrize("postcode, expected", [
    ('ZE1 0AA', 'S12000027'),
    ('ZE10AA', 'S12000027'),
    ('ze1 0aa', 'S12000027'),
    (None, None)
])
def test_merge_postcodes(postcode, expected):
    df = pd.DataFrame([postcode], columns=["HOME_POST"])
    df = merge_postcodes(df, "HOME_POST")
    if expected is None:
        assert np.isnan(df.laua[0])
    else:
        assert df.laua[0] == expected
