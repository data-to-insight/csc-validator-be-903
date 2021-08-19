from copy import copy
from collections import defaultdict
from dataclasses import asdict
from typing import Any, List, Dict
from .types import UploadedFile
from .ingress import read_from_text, read_postcodes
from .config import configured_errors

def run_validation_for_javascript(uploaded_files: List[UploadedFile], error_codes: List[str], metadata: Dict[str, Any]):
    """
    External API - this is the main entrypoint for the frontend. 

    Returned values are designed to be Javascript friendly, so that toJs can be called.

    :param uploaded_files: a list of file information with name, description and fileText - should have .to_py() called before passing
    :param error_codes: a list of error codes to filter for when validating - should have .to_py() called before passing
    :returns: The relevant data in the form
      - js_files - A list of {row header: row value} dictionaries, one for each row.
      - errors - A list of all configured error definitions, as dictionaries.
      - error_definitions - A nested dictionary of {file name -> index in file -> list of error codes} 
    """
    dfs = read_from_text(raw_files=uploaded_files)
        
    js_files = {k: [t._asdict() for t in df.itertuples(index=True)] for k, df in dfs.items()}

    handle = copy(dfs)
    handle['metadata'] = _process_metadata(metadata)
    validated = [(error, f(handle)) for error, f in configured_errors if error.code in error_codes]

    # Passed to JS
    error_definitions = {e.code: asdict(e) for e, _ in validated}

    errors = {file_name: defaultdict(list) for file_name in dfs}
    for error, error_incidences in validated:
        for file_name, locations in error_incidences.items():
            for location in locations:
                errors[file_name][int(location)].append(error.code)

    return js_files, errors, error_definitions

def get_error_definitions_list():
    """
    External API - this is the other entrypoint for the frontend.

    This is a simple function to return the list of all configured errors, so that end users can filter to their use case.
    """
    return [e for e, _ in configured_errors]

def _process_metadata(metadata):
    metadata['postcodes'] = read_postcodes(metadata['postcodes'])
    return metadata