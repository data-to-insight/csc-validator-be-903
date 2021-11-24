#!/usr/bin/env python
import argparse
import logging
import qlacref_authorities

from validator903.config import errors as all_configured_errors
from validator903.validator import Validator
from validator903.report import Report
from validator903.ingress import read_files


def main(files, errors):
    metadata = {
        'localAuthority': qlacref_authorities.records[0]['UTLA21CD'],
        'collectionYear': '2020/21',
    }
    validator = Validator(metadata=metadata, files=read_files(files))

    if errors == "all":
        errors = all_configured_errors.keys()
    else:
        errors = [e.strip() for e in errors.split(',')]

    result = validator.validate(error_codes=errors)
    report = Report(result)

    report.excel_report('report.xlsx')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate files and write validation report")
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help="Filenames to validate")
    parser.add_argument(
        '--errors', '-e', type=str, nargs='?', default='all', help="Error codes separated with a comma"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    main(**vars(args))
