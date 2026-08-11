import io

import pytest

from katakana_eigo import cli
from katakana_eigo.cli import convert_text, convert_word, main


def test_convert_word_known_word():
    assert convert_word("hello") == "ハロウ"


def test_convert_word_falls_back_when_no_phonemes(monkeypatch):
    monkeypatch.setattr(cli, "word_to_phonemes", lambda word: [])
    assert convert_word("whatever") == "whatever"


def test_convert_word_falls_back_on_unexpected_error(monkeypatch):
    def boom(word):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "word_to_phonemes", boom)
    assert convert_word("hello") == "hello"


def test_convert_text_preserves_layout_and_non_word_text():
    text = "Can't get no sleep\ntonight、ですね"
    result = convert_text(text)
    assert result.startswith(convert_word("Can't"))
    assert "\n" in result
    assert "ですね" in result
    assert "、" in result


def test_main_reads_from_stdin_and_writes_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("hello world"))
    exit_code = main([])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert out == convert_text("hello world")


def test_main_reads_from_file(tmp_path, capsys):
    file_path = tmp_path / "input.txt"
    file_path.write_text("hello world", encoding="utf-8")
    exit_code = main([str(file_path)])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert out == convert_text("hello world")


def test_main_missing_file_returns_1_and_prints_error(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    exit_code = main([str(missing)])
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "ファイルが見つかりません" in err
    assert str(missing) in err


def test_main_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "katakana-eigo" in out


def test_main_stdin_invalid_utf8_returns_1_and_prints_error(monkeypatch, capsys):
    bad_stdin = io.TextIOWrapper(io.BytesIO(b"hello \xff world"), encoding="utf-8")
    monkeypatch.setattr("sys.stdin", bad_stdin)
    exit_code = main([])
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "標準入力をUTF-8として読み込めません" in err


def test_main_file_invalid_utf8_returns_1_and_prints_error(tmp_path, capsys):
    file_path = tmp_path / "bad.txt"
    file_path.write_bytes(b"hello \xff world")
    exit_code = main([str(file_path)])
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "ファイルを読み込めません" in err
    assert str(file_path) in err


def test_convert_word_hyphenated_compound_is_single_conversion():
    assert convert_word("well-known") == "ウェルノウン"


def test_convert_text_alphanumeric_and_hyphenated_words_not_split():
    text = "This well-known tool handles COVID-19 and phone 123-456 fine."
    result = convert_text(text)
    assert "ウェルノウン" in result
    # 数字のみの文字列("123-456")は英単語とみなさず、変更せず残る。
    assert "123-456" in result
    # ハイフン複合語・英数字混在語は分割されず、ハイフン自体は出力に残らない。
    assert "well-" not in result
    assert "-known" not in result
    assert "COVID-" not in result
