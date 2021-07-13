from collections import defaultdict
from dataclasses import asdict
from typing import List, Dict
from .types import UploadedFile
from .ingress import read_from_text
from .config import tested_errors

def run_validation_for_javascript(uploaded_files: List[UploadedFile]):
    """
    External API - this is the entrypoint for the frontend. 

    Returned values are designed to be Javascript friendly, so that toJs can be called.

    :param uploaded_files: - should have .to_py()
    :returns: The relevant data in the form
      - js_files - A list of {row header: row value} dictionaries, one for each row.
      - errors - A list of all configured error definitions, as dictionaries.
      - error_definitions - A nested dictionary of {file name -> index in file -> list of error codes} 
    """
    dfs = read_from_text(raw_files=uploaded_files)
        
    js_files = {k: [t._asdict() for t in df.itertuples(index=True)] for k, df in dfs.items()}

    validated = [(error, f(dfs)) for error, f in tested_errors]

    # Passed to JS
    error_definitions = {e.code: asdict(e) for e, _ in validated}

    errors = {file_name: defaultdict(list) for file_name in dfs}
    for error, error_incidences in validated:
        for file_name, locations in error_incidences.items():
            for location in locations:
                errors[file_name][int(location)].append(error.code)

    return js_files, errors, error_definitions

def get_error_definitions_list():
    return [e for e, _ in tested_errors]