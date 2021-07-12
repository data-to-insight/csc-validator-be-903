from dataclasses import dataclass
from typing import Type, TypedDict

@dataclass
class ErrorDefinition:
    code: str
    description: str
    affected_fields: list[str]


class UploadedFile(TypedDict):
    name: str
    fileText: str
    description: str

class UploadException(Exception):
    pass
