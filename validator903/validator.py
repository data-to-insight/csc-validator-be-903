import logging
from typing import Any, List, Dict
from pandas import DataFrame

from .types import UploadedFile
from .ingress import read_from_text
from .config import configured_errors
from .datastore import copy_datastore, create_datastore

logger = logging.getLogger(__name__)


class Validator:
    dfs: Dict[str, DataFrame] = {}

    def __init__(self, metadata: Dict[str, Any], files: List[UploadedFile]):
        self.metadata = metadata
        logger.info('Reading uploaded files...')
        self.dfs.update(read_from_text(raw_files=files))

    def validate(self, error_codes: List[str]):
        logger.info('Creating Data Store...')
        data_store = create_datastore(self.dfs, self.metadata)

        ds_results = copy_datastore(data_store)
        for error, test_func in configured_errors:
            if error.code in error_codes:
                logger.info(f'Validating error {error.code}...')
                ds_copy = copy_datastore(data_store)
                result: Dict[str, List[Any]] = test_func(ds_copy)
                for table, values in result.items():
                    if len(values) > 0:
                        logger.debug(f"Test {error.code} found {len(values)} errors")
                        ds_results[table].loc[values, f'ERR_{error.code}'] = True

        return ds_results
