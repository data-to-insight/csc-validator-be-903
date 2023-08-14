import pytest
import os
from lac_validator.ingress import (
    read_csvs_from_text,
    read_from_text,
    read_xml_from_text,
    construct_provider_info_table,
)
from lac_validator.types import UploadError, UploadedFile
import pandas as pd


class Test_read_from_text:
    @pytest.mark.parametrize("files", [pytest.param([])])
    def test_read_from_text_errors(self, files):
        with pytest.raises(UploadError):
            read_from_text(files)

    def test_csv_reading(self, mocker):
        read_csv = mocker.patch("lac_validator.ingress.read_csvs_from_text")
        files: list[UploadedFile] = [
            {"name": "header.csv", "file_content": "", "description": ""}
        ]
        read_from_text(files)
        read_csv.assert_called_once_with(files)

    def test_xml_reading(self, mocker):
        read_xml = mocker.patch("lac_validator.ingress.read_xml_from_text")
        files: list[UploadedFile] = [
            {"name": "data.xml", "file_content": "test_text", "description": ""}
        ]
        read_from_text(files)
        read_xml.assert_called_once_with("test_text")


def test_read_csv_from_text(dummy_input_files):
    csv_path_dir = os.path.join(os.path.dirname(__file__), "fake_data")

    def read_file(path):
        with open(path) as f:
            return f.read().encode()

    uploaded_files = [
        {
            "file_content": read_file(os.path.join(csv_path_dir, file_name)),
            "description": "This year",
        }
        for file_name in dummy_input_files
    ]

    last_year_files = [
        {"file_content": d["file_content"], "description": "Prev year"}
        for d in uploaded_files
    ]
    uploaded_files += last_year_files

    out = read_csvs_from_text(uploaded_files)
    assert len(out) == 2 * len(dummy_input_files)
    for name, val in out.items():
        if name in ("Header", "Header_last"):
            assert "UASC" in val.columns, f"UASC field not added to {name}"
        assert len(val) > 0, f"No entries found for {name}"
        assert set(str(dtype) for dtype in val.dtypes) == {
            "object"
        }, f"Got non-object columns in {name}: \n{val.dtypes}!"


def test_read_xml_from_text():
    xml_path = os.path.join(os.path.dirname(__file__), "fake_data", "fake_903.xml")
    with open(xml_path) as f:
        data = f.read()

    out = read_xml_from_text(data)

    for name, val in out.items():
        assert len(val) > 0, f"No entries found for {name}"
        assert set(str(dtype) for dtype in val.dtypes) == {
            "object"
        }, f"Got non-objects columns in {name}: \n{val.dtypes}!"


def test_construct_provider_info_table(ch_path, scp_path):
    output = construct_provider_info_table(ch_path, scp_path)
    test_df = pd.DataFrame(cloumns=['URN', 'LA_NAME_FROM_FILE', 'PLACE_CODES', 'PROVIDER_CODES', 'REG_END', 'POSTCODE', 'source', 'LA_CODE_INFERRED', 'LA_NAME_INFERRED'])

    print(output)
