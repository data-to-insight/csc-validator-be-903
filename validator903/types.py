from dataclasses import dataclass
from typing import List, TypedDict

@dataclass
class ErrorDefinition:
    """
    Error definition information that is passed onto the frontend tool. The code and description are used for display, 
    and the affected_fields is a list of fields which will be highlighted by the frontend tool if present.

    :param code: String describing the error code e.g. '103'
    :param description: String describing the error (from guidance) e.g. 'The ethnicity code is either not valid or has not been entered'
    :param affected_fields: A list of fields to highlight in the tool e.g. ['ETHNIC']
    """
    code: str
    description: str
    affected_fields: List[str]


class UploadedFile(TypedDict):
    name: str
    fileText: str
    description: str

class UploadException(Exception):
    pass
