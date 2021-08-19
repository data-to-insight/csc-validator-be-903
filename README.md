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

### Updating postcodes

To update postcodes, use the `scripts/create_postcode_db.py` script.

This requires data from the latest ONS postcode file - the National Statistics Postcode Lookup. An example file is (here)[https://geoportal.statistics.gov.uk/datasets/ons::national-statistics-postcode-lookup-may-2021/about].

You will need to update the filenames in the script. This will then output `la_data.json` and `postcodes.zip`. These then need to be bundled with the [frontend code](https://github.com/SocialFinanceDigitalLabs/quality-lac-data-beta) - this will be done by a maintainer of both repositories. Reach out to Social Finance if needed.