import pytest
from validator903.ingress import read_from_text
from validator903.types import UploadException

class Test_read_from_text:
    @pytest.mark.parametrize("files", [
        pytest.param([])
    ])
    def test_read_from_text_errors(self, files):
        with pytest.raises(UploadException):
            read_from_text(files)