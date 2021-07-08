from dataclasses import dataclass
from typing import List

@dataclass
class ErrorDefinition:
    code: str
    description: str
    affected_fields: List[str]

class UploadException(Exception):
    pass
