from dataclasses import dataclass
from typing import List, TypedDict

@dataclass
class ErrorDefinition:
    code: str
    description: str
    affected_fields: List[str]


class UploadedFile(TypedDict):
    name: str
    fileText: str
    description: str

class UploadException(Exception):
    pass
