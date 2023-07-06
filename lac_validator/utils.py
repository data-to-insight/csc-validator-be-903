from validator903.types import UploadedFile, UploadError
from prpc_python.pyodide import PyodideFile
from io import TextIOWrapper

# list[UploadedFile | PyodideFile | str] is syntax that is available only in python 3.10
# TODO update to python3.10 there is no particular reason why this project needs to be 3.9

def process_uploaded_files(input_files:dict[str, list]):
    """
    :param dict frontend_file_dict: dict of lists showing file content and the field into which user uploaded file.

    :return: files of UploadedFile type as ingress.read_from_text expects.
    """
    # children's homes field: "description" == "CH lookup"
    # social care providers field: "description" == "SCP lookup"
    # current year: description="This year"
    # Previous year: description="Prev year"

    uploaded_files = []
    for field_name, file_refs in input_files.items():
        for file_ref in file_refs:
            # name attribute depends on whether on file type. CLI and API send different types.
            if isinstance(file_ref, PyodideFile):         
                # PyodideFile from frontend
                filename = file_ref.filename
                file_text = file_ref.read()
            else:
                if isinstance(file_ref, TextIOWrapper):
                    # Text IO wrapper object from command line
                    filename = file_ref.name                   
                elif isinstance(file_ref, str):
                    # string path
                    filename = file_ref
                else:
                    raise UploadError("file format is not recognised.") 
                              
                with open(filename, "rb") as f:
                    file_text = f.read() 
                
            # TODO convert all dict statements to use UploadedFile
            uploaded_files.append(UploadedFile(name=filename, description=field_name, file_content=file_text))
    return uploaded_files
