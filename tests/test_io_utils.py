import io

import pytest

from katakana_eigo.io_utils import read_input, write_output


def test_read_input_from_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("hello from stdin"))
    assert read_input(None) == "hello from stdin"


def test_read_input_from_file(tmp_path):
    file_path = tmp_path / "input.txt"
    file_path.write_text("hello from file", encoding="utf-8")
    assert read_input(str(file_path)) == "hello from file"


def test_read_input_from_file_preserves_utf8(tmp_path):
    file_path = tmp_path / "input.txt"
    file_path.write_text("こんにちは a pen です", encoding="utf-8")
    assert read_input(str(file_path)) == "こんにちは a pen です"


def test_read_input_missing_file_raises(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        read_input(str(missing))


def test_write_output_writes_to_stdout(monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr("sys.stdout", buffer)
    write_output("カタカナ")
    assert buffer.getvalue() == "カタカナ"


def test_read_input_from_stdin_invalid_utf8_raises(monkeypatch):
    bad_stdin = io.TextIOWrapper(io.BytesIO(b"hello \xff world"), encoding="utf-8")
    monkeypatch.setattr("sys.stdin", bad_stdin)
    with pytest.raises(UnicodeDecodeError):
        read_input(None)


def test_read_input_from_file_invalid_utf8_raises(tmp_path):
    file_path = tmp_path / "bad.txt"
    file_path.write_bytes(b"hello \xff world")
    with pytest.raises(UnicodeDecodeError):
        read_input(str(file_path))
