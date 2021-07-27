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
python setup.py bdist_wheel
```

Right now this is manually copied into the frontend repo. Eventually this will be ran automatically.

### Local installation

To install, first clone the repo and move into the directory. Then run

```
pip install -e .
```