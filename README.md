# Quality LAC data beta: Python validator
[![Run on Repl.it](https://repl.it/badge/github/SocialFinanceDigitalLabs/quality-lac-data-beta-validator)](https://repl.it/github/SocialFinanceDigitalLabs/quality-lac-data-beta-validator)

Python-side code for the Quality LAC Data Beta frontend

This is designed to work in tandem with the frontend, but can also be used as an individual package.

It provides methods of finding the validation errors defined by the DfE in 903 data.

### Project Structure

```
project
│   setup.py
├───validator903
        api.py              - Interface with Javascript
        config.py           - High-level configuration
        ingress.py          - Data ingress (handling CSV and XML files)
        types.py            - Classes used across the work
        validators.py       - All individual validator codes
```

Most of the work from contributors will be in `validators.py`.


### Building a wheel for Pyodide

Pyodide requires a pure Python wheel. To build one, clone the repo and move it into the directory. Then run

```
poetry build
```

Right now this is manually copied into the frontend repo. Eventually this will be ran automatically.

### Local installation

To install, first clone the repo and move into the directory. Then run

```
poetry install
```

### The input data

Below is the template for the input data that is given to each validator (the `dfs` object). You should assume that not all of these keys are present and handle that appropriately.

Any XML uploads are converted into CSV form to give the same inputs.

```
{
    # This years data
    'Header':   # header dataframe
    'Episodes': # episodes dataframe
    'Reviews':  # reviews dataframe
    'UASC':     # UASC dataframe
    'OC2':      # OC2 dataframe
    'OC3':      # OC3 dataframe
    'AD1':      # AD1 dataframe
    'PlacedAdoption':  # Placed for adoption dataframe
    'PrevPerm': # Previous permanence dataframe
    'Missing':  # Missing dataframe
    # Last years data
    'Header_last':   # header dataframe
    'Episodes_last': # episodes dataframe
    'Reviews_last':  # reviews dataframe
    'UASC_last':     # UASC dataframe
    'OC2_last':      # OC2 dataframe
    'OC3_last':      # OC3 dataframe
    'AD1_last':      # AD1 dataframe
    'PlacedAdoption_last':  # Placed for adoption dataframe
    'PrevPerm_last': # Previous permanence dataframe
    'Missing_last':  # Missing dataframe
    # Metadata
    'metadata': {
        'collection_start': # A datetime with the collection start date (year/4/1)
        'collection_end':   # A datetime with the collection end date (year + 1/4/1)
        'postcodes':        # Postcodes dataframe, columns laua, oseast1m, osnrth1m, pcd
        'localAuthority:    # The local authority code entered (long form, e.g. E07000026)
        'collectionYear':   # The raw collection year string - unlikely to need this (e.g. '2019/20')
    }
}
```

### Updating postcodes

To update postcodes, use the `scripts/create_postcode_db.py` script.

This requires data from the latest ONS postcode file - the National Statistics Postcode Lookup. An example file is [here](https://geoportal.statistics.gov.uk/datasets/ons::national-statistics-postcode-lookup-may-2021/about).

You will need to update the filenames in the script. This will then output `la_data.json` and `postcodes.zip`. These then need to be bundled with the [frontend code](https://github.com/SocialFinanceDigitalLabs/quality-lac-data-beta) - this will be done by a maintainer of both repositories. Reach out to Social Finance if needed.