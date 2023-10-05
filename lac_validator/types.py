from typing import TypedDict


class UploadedFile(TypedDict):
    name: str
    file_content: bytes
    description: str


class UploadError(Exception):
    pass


class MissingMetadataError(KeyError):
    pass
