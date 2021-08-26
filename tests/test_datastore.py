from validator903.datastore import create_datastore

def test_create_datastore(dummy_input_data, dummy_postcodes):
    metadata = {
        'postcodes': dummy_postcodes,
        'collectionYear': '2019/20',
    }
    ds = create_datastore(dummy_input_data, metadata)

    assert ds['metadata'] == metadata 