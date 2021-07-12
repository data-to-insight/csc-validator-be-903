import pytest
from validator903.ingress import read_from_text
from validator903.types import UploadException, UploadedFile

class Test_read_from_text:
    @pytest.mark.parametrize("files", [
        pytest.param([])
    ])
    def test_read_from_text_errors(self, files):
        with pytest.raises(UploadException):
            read_from_text(files)

    def test_csv_reading(self, mocker):
        read_csv = mocker.patch('validator903.ingress.read_csvs_from_text')
        files: list[UploadedFile] = [{'name': 'header.csv', 'fileText': '', 'description': ''}]
        read_from_text(files)
        read_csv.assert_called_once_with(files)

    def test_xml_reading(self, mocker):
        read_xml = mocker.patch('validator903.ingress.read_xml_from_text')
        files: list[UploadedFile] = [{'name': 'data.xml', 'fileText': 'test_text', 'description': ''}]
        read_from_text(files)
        read_xml.assert_called_once_with('test_text')