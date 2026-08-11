"""標準入力/ファイルからの読み込みと、標準出力への書き出し。"""

import sys


def _force_utf8(stream):
    # sys.stdin/stdout はOS/ロケール依存のエンコーディング(Windowsでは既定でcp932等)
    # になっている場合があるため、UTF-8に強制する。errors="strict" を明示することで、
    # 不正なUTF-8バイト列は読み捨てずに UnicodeDecodeError として送出させる。
    # テストで io.StringIO 等の差し替えストリームを渡す場合は reconfigure を
    # 持たないため何もしない。
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="strict")


def read_input(path: str | None) -> str:
    """テキストを読み込む。

    `path` が None の場合は標準入力から、指定されている場合はそのファイルから
    UTF-8で全文を読み込む。ファイルが存在しない/読み込めない場合は
    `OSError`(`FileNotFoundError` 等その派生)が、UTF-8として不正なバイト列を
    含む場合は `UnicodeDecodeError` がそのまま送出される。
    """
    if path is None:
        _force_utf8(sys.stdin)
        return sys.stdin.read()
    with open(path, encoding="utf-8", errors="strict") as f:
        return f.read()


def write_output(text: str) -> None:
    """変換後のテキストを標準出力に書き出す。"""
    _force_utf8(sys.stdout)
    sys.stdout.write(text)
