import pytest

from jobly.services.cv_parser import extract_text_from_pdf


def test_extract_text_invalid_pdf():
    with pytest.raises(Exception):
        extract_text_from_pdf(b"not a pdf")
