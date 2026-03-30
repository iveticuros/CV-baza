from __future__ import annotations

import pytest

from app.services.file_storage import save_cv_file, is_pdf_magic, delete_cv_file, read_cv_file


class TestPdfValidation:
    def test_valid_pdf_magic(self):
        assert is_pdf_magic(b"%PDF-1.4 content")

    def test_invalid_magic(self):
        assert not is_pdf_magic(b"not a pdf")

    def test_empty_header(self):
        assert not is_pdf_magic(b"")


class TestSaveCvFile:
    def test_rejects_non_pdf_content(self):
        with pytest.raises(ValueError, match="PDF"):
            save_cv_file(user_id=1, content=b"not a pdf file content", original_filename="test.txt")

    def test_rejects_wrong_mime_type(self):
        pdf_content = b"%PDF-1.4 fake pdf content"
        with pytest.raises(ValueError, match="PDF"):
            save_cv_file(
                user_id=1, content=pdf_content,
                original_filename="test.pdf", content_type="text/plain",
            )

    def test_rejects_oversized_file(self):
        pdf_content = b"%PDF" + b"x" * (5 * 1024 * 1024 + 1)
        with pytest.raises(ValueError, match="prevelik"):
            save_cv_file(user_id=1, content=pdf_content, original_filename="big.pdf")

    def test_save_and_read_cycle(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.services.file_storage.settings.CV_STORAGE_DIR", str(tmp_path))
        pdf_content = b"%PDF-1.4 test content here"
        stored_name, orig = save_cv_file(
            user_id=42, content=pdf_content,
            original_filename="my_cv.pdf", content_type="application/pdf",
        )
        assert stored_name.endswith(".pdf")
        assert orig == "my_cv.pdf"
        data = read_cv_file(stored_name)
        assert data == pdf_content

    def test_delete_cv(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.services.file_storage.settings.CV_STORAGE_DIR", str(tmp_path))
        pdf_content = b"%PDF-1.4 to delete"
        stored_name, _ = save_cv_file(
            user_id=1, content=pdf_content, original_filename="del.pdf",
        )
        delete_cv_file(stored_name)
        with pytest.raises(FileNotFoundError):
            read_cv_file(stored_name)
