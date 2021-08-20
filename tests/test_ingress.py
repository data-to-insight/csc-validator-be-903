import pytest
import os
from validator903.ingress import read_csvs_from_text, read_from_text, read_xml_from_text
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

def test_read_csv_from_text(dummy_input_files):
    csv_path_dir = os.path.join(os.path.dirname(__file__), 'fake_data')

    def read_file(path):
        with open(path) as f:
            return f.read()

    uploaded_files = [{
        'fileText': read_file(os.path.join(csv_path_dir, file_name)),
        'description': 'This year',
    } for file_name in dummy_input_files]
    
    last_year_files = [{'fileText': d['fileText'], 'description': 'Last year'} for d in uploaded_files]
    uploaded_files += last_year_files

    out = read_csvs_from_text(uploaded_files)
    assert len(out) == 2 * len(dummy_input_files) 
    for name, val in out.items():
        assert len(val) > 0, f'No entries found for {name}'


def test_read_xml_from_text():
    xml_path = os.path.join(os.path.dirname(__file__), 'fake_data', 'fake_903.xml')
    with open(xml_path) as f:
        data = f.read()

    out = read_xml_from_text(data)

    for name, val in out.items():
        assert len(val) > 0, f'No entries found for {name}'
    