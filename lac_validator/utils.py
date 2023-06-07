
def process_uploaded_files(frontend_files_dict):
    """
    :param dict frontend_file_dict: dict of lists showing file content and the field into which user uploaded file.

    :return: files of UploadedFile type as ingress.read_from_text expects.
    """
    # children's homes field: "description" == "CH lookup"
    # social care providers field: "description" == "SCP lookup"
    # current year: description="This year"
    # Previous year: description="Prev year"

    files = []
    for field_name in frontend_files_dict:
        for file_ref in frontend_files_dict[field_name]:
            # name attribute depends on whether on file type. CLI and API send different types.
            try:                
                # PyodideFile from frontend
                filename = file_ref.filename
                file_text = file_ref.read()
            except:
                try:
                    # Text IO wrapper object from command line
                    filename = file_ref.name                    
                except:
                    # string path
                    filename = file_ref

                with open(filename, "rb") as f:
                    file_text = f.read()

            files.append(dict(name=filename, description=field_name, file_content=file_text))
    return files
