import os

import pytest

from lac_validator.ingress import (
    read_csvs_from_text,
    read_from_text,
    read_xml_from_text,
    construct_provider_info_table,
    combined_ch_scp_check,
    scpch_provider_info_table,
)
from lac_validator.types import UploadError, UploadedFile

"""
Tests can be run in the CLI, once inside poetry shell, using:
poetry run coverage run --data-file='.coverage.framework' -m pytest
"""


class Test_read_from_text:
    @pytest.mark.parametrize("files", [pytest.param([])])
    def test_read_from_text_errors(self, files):
        with pytest.raises(UploadError):
            read_from_text(files)

    def test_csv_reading(self, mocker):
        read_csv = mocker.patch("lac_validator.ingress.read_csvs_from_text")
        construct_info = mocker.patch(
            "lac_validator.ingress.construct_provider_info_table"
        )
        combined_scpch_check = mocker.patch(
            "lac_validator.ingress.combined_ch_scp_check"
        )
        scpch_provider_info_table = mocker.patch(
            "lac_validator.ingress.scpch_provider_info_table"
        )

        files: list[UploadedFile] = [
            {"name": "header.csv", "file_content": "", "description": ""},
            {"name": "ch_lookup.csv", "file_content": "", "description": "CH lookup"},
            {"name": "scp_lookup.csv", "file_content": "", "description": "SCP lookup"},
        ]

        head = files[0]
        ch = files[1]
        scp = files[2]

        read_from_text(files)
        read_csv.assert_called_once_with([head])
        construct_info.assert_called_once_with(CH=ch, SCP=scp)

        # Test ingress for one CH upload to check if it's the combined form
        files: list[UploadedFile] = [
            {"name": "header.csv", "file_content": "", "description": ""},
            {
                "name": "ch_lookup.csv",
                "file_content": "test",
                "description": "CH lookup",
            },
        ]

        head = files[0]
        ch = files[1]

        read_from_text(files)
        combined_scpch_check.assert_called_once_with(ch)
        scpch_provider_info_table.assert_called_once_with(scpch=ch)

        # Test ingress for one SCP upload to check if it's the combined form
        files: list[UploadedFile] = [
            {"name": "header.csv", "file_content": "", "description": ""},
            {"name": "scp_lookup.csv", "file_content": "", "description": "SCP lookup"},
        ]

        with pytest.raises(UploadError):
            read_from_text(files)

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


def test_construct_provider_info_table(dummy_chscp):
    """Tests childrens home and social care providers form ingress as both forms
    and as filepaths to the location of the files."""
    expected_columns = [
        "URN",
        "LA_NAME_FROM_FILE",
        "PLACE_CODES",
        "PROVIDER_CODES",
        "REG_END",
        "POSTCODE",
        "source",
        "LA_CODE_INFERRED",
        "LA_NAME_INFERRED",
    ]

    ch = {}
    scp = {}
    combined = {}
    combined_assisted = {}
    (
        ch["file_content"],
        scp["file_content"],
        ch_path_dir,
        scp_path_dir,
        combined_path_dir,
        combined["file_content"],
        combined_assisted["file_content"],
    ) = dummy_chscp

    output_from_string = construct_provider_info_table(ch_path_dir, scp_path_dir)
    string_output_columns = output_from_string.columns.to_list()

    assert string_output_columns == expected_columns

    output_from_file = construct_provider_info_table(ch, scp)
    file_output_columns = output_from_file.columns.to_list()
    assert file_output_columns == expected_columns


def test_combined_ch_scp_check(dummy_chscp):
    ch = {}
    scp = {}
    combined = {}
    combined_assisted = {}
    (
        ch["file_content"],
        scp["file_content"],
        ch_path_dir,
        scp_path_dir,
        combined_path_dir,
        combined["file_content"],
        combined_assisted["file_content"],
    ) = dummy_chscp

    with pytest.raises(UploadError):
        combined_ch_scp_check(scp["file_content"])

    with pytest.raises(UploadError):
        combined_ch_scp_check(ch["file_content"])

    combined_outcome = combined_ch_scp_check(combined["file_content"])
    assert combined_outcome == True

    combined_assisted_outcome = combined_ch_scp_check(combined_assisted["file_content"])
    assert combined_assisted_outcome == True


def test_scpch_provider_info_table(dummy_chscp):
    expected_columns = [
        "URN",
        "LA_NAME_FROM_FILE",
        "PLACE_CODES",
        "PROVIDER_CODES",
        "REG_END",
        "POSTCODE",
        "source",
        "LA_CODE_INFERRED",
        "LA_NAME_INFERRED",
    ]

    combined = {}
    combined_assisted = {}
    (
        ch,
        scp,
        ch_path_dir,
        scp_path_dir,
        combined_path_dir,
        combined["file_content"],
        combined_assisted["file_content"],
    ) = dummy_chscp

    output = scpch_provider_info_table(combined)
    output_columns = output.columns.to_list()
    assert output_columns == expected_columns
