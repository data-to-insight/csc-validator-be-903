import logging
import datetime
from typing import Any, List, Dict
from pandas import DataFrame

from .types import UploadedFile
from .ingress import read_from_text
from .config import configured_errors
from .datastore import copy_datastore, create_datastore

logger = logging.getLogger(__name__)
handler = logging.FileHandler(datetime.datetime.now().strftime('903 Validator -- %d-%m-%Y %H.%M.%S.log'))
handler.setLevel(logging.DEBUG)

f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(f_format)
logger.addHandler(handler)


class Validator:
    dfs: Dict[str, DataFrame] = {}

    def __init__(self, metadata: Dict[str, Any], files: List[UploadedFile]):
        self.metadata = metadata
        logger.info('Reading uploaded files...')
        self.dfs.update(read_from_text(raw_files=files))

    def validate(self, error_codes: List[str]):
        logger.info('Creating Data Store...')
        data_store = create_datastore(self.dfs, self.metadata)

        checks_that_failed_to_run = []
        checks_skipped_coz_missing_tables = []

        ds_results = copy_datastore(data_store)
        for error, test_func in configured_errors:
            if error.code in error_codes:
                logger.info(f'Validating error {error.code}...')
                ds_copy = copy_datastore(data_store)
                try:
                    result: Dict[str, List[Any]] = test_func(ds_copy)
                except Exception as e:
                    logger.exception(f"Error check {error.code} failed to run!")
                    checks_that_failed_to_run.append(error.code)
                    continue

                if result == {}:
                    checks_skipped_coz_missing_tables.append(error.code)

                for table, values in result.items():
                    if len(values) > 0:
                        logger.debug(f"Test {error.code} found {len(values)} errors")
                        ds_results[table].loc[values, f'ERR_{error.code}'] = True
        return ds_results
