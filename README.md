# Quality LAC data beta: Python validator

![Build & Test](https://github.com/SocialFinanceDigitalLabs/quality-lac-data-beta-validator/actions/workflows/run-tests.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/quality-lac-data-validator.svg)](https://badge.fury.io/py/quality-lac-data-validator)
[![Run on Repl.it](https://repl.it/badge/github/SocialFinanceDigitalLabs/quality-lac-data-beta-validator)](https://repl.it/github/SocialFinanceDigitalLabs/quality-lac-data-beta-validator)

*We want to build a tool that improves the quality of data on Looked After Children so that Children’s Services Departments have all the information needed to enhance their services.*

We believe that a tool that highlights and helps fixing data errors would be valuable for:

1.   Reducing the time analysts, business support and social workers spend cleaning data.
2.   Enabling leadership to better use evidence in supporting Looked After Children.

## About this project

The aim of this project is to deliver a tool to relieve some of the pain-points
of [reporting and quality][qlac-blog] in children's services data. This project
focuses, in particular, on data on looked after children (LAC) and the
[SSDA903][dfe-903] return.

The project consists of a number of related pieces of work:

* [Hosted Tool][qlac]
* [React & Pyodie Front-End][qlac-front-end]
* [Python Validator Engine & Rules][qlac-engine] [this repo]
* [Local Authority Reference Data][qlac-ref-la]
* [Postcode Reference Data][qlac-ref-pc]

The core parts consist of a [Python][python] validator engine and rules using
[Pandas][pandas] with [Poetry][poetry] for dependency management. The tool is targeted
to run either standalone, or in [pyodide][pyodide] in the browser for a zero-install
deployment with offline capabilities.

It provides methods of finding the validation errors defined by the DfE in 903 data.
The validator needs to be provided with a set of input files for the current year and,
optionally, the previous year. These files are coerced into a common format and sent to
each of the validator rules in turn. The validators report on rows not meeting the rules
and a report is provided highlight errors for each row and which fields were included in
the checks.

## Data pipeline

* Loading of files
* Identification of tables - currently matched on **exact** filename
* Conversion of CSV to tabular format - **no type checking**
* Enrichment of provided data with Postcode distances
* Evaluation of rules
* Report

### Project Structure

These are the key files

```
project
├─── pyproject.toml           - Project details and dependencies
├─── validator903
│    ├─── config.py           - High-level configuration
│    ├─── ingress.py          - Data ingress (handling CSV and XML files)
│    ├─── types.py            - Classes used across the work
│    ├─── validator.py        - The core validator process
│    └─── validators.py       - All individual validator codes
└─── tests                    - Unit tests
```

Most of the work from contributors will be in `validators.py` and the associated testing files under
tests. Please do not submit a pull-request without a comprehensive test.

### Development

To install the code and dependencies. Then from the main project directory run

```
poetry install
```

### Adding validators

Validators are simple functions, usually called `validate_XXX()` which take no arguments and
return a tuple of an `ErrorDefinition` and a test function. The test function itself takes
a single argument, the *datastore*, which is a [Mapping][py-mapping] (a dict-like) following the structure below.

The following is the expected structure for the input data that is given to each validator (the `dfs` object).
You should assume that not all of these keys are present and handle that appropriately.

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

## Releases

To build and release a new version, make sure all your unit tests pass.

We use [semantic versioning][semver], so update the project version in [pyproject.toml](./pyproject.toml) accordingly
and commit, creating a PR. Once the release version is on GitHub, create a GitHub release naming the release with the 
current release name, e.g. 1.0 and the tag with the release name prefixed with a v, i.e. v1.0. Alpha and beta releases 
can be flagged by appending `-alpha.<number>` and `-beta.<number>`.


[qlac-blog]: https://www.socialfinance.org.uk/blogs/better-data-children-care-building-common-approach
[dfe-903]: https://www.gov.uk/guidance/children-looked-after-return-guide-to-submitting-data

[python]: https://www.python.org/
[pandas]: https://pandas.pydata.org/
[poetry]: https://python-poetry.org/
[pyodide]: https://pyodide.org/en/stable/
[semver]: https://semver.org/

[qlac]: https://sfdl.org.uk/quality-lac-data-beta/
[qlac-front-end]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-beta
[qlac-engine]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-beta-validator
[qlac-ref-la]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-authorities
[qlac-ref-pc]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-postcodes

[py-mapping]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping
