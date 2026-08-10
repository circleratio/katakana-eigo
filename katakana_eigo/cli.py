"""CLIエントリポイント。読み込み→トークン分割→発音解決→カタカナ変換→出力を統合する。"""

import argparse
import sys
import traceback

from katakana_eigo.io_utils import read_input, write_output
from katakana_eigo.kana import phonemes_to_kana
from katakana_eigo.pronounce import word_to_phonemes
from katakana_eigo.tokenizer import tokenize


def convert_word(word: str) -> str:
    """英単語1語をカタカナに変換する。変換できない場合は元の単語を返す。"""
    try:
        phonemes = word_to_phonemes(word)
        if not phonemes:
            return word
        kana = phonemes_to_kana(phonemes)
        return kana or word
    except Exception:
        return word


def convert_text(text: str) -> str:
    """テキスト中の英単語だけをカタカナに変換し、他はそのまま残す。"""
    parts = [
        convert_word(token.text) if token.is_word else token.text
        for token in tokenize(text)
    ]
    return "".join(parts)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="katakana-eigo",
        description="英語の文章を、実際の発音に近いカタカナ表記に変換するCLIフィルタ。",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="変換対象の英語テキストファイル(省略時は標準入力から読み込む)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        text = read_input(args.file)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {args.file}", file=sys.stderr)
        return 1
    except OSError:
        print(f"エラー: ファイルを読み込めません: {args.file}", file=sys.stderr)
        return 1

    try:
        write_output(convert_text(text))
    except Exception:
        traceback.print_exc()
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
