"""入力テキストを英単語トークンとそれ以外のトークンに分割する。"""

import re
from dataclasses import dataclass

# 英数字の連続をアポストロフィ・ハイフンで連結した範囲を1トークン候補として
# 切り出す。アポストロフィ・ハイフンは英数字に挟まれる位置にのみマッチするため、
# 文中のダッシュ記号や行末ハイフンを誤って取り込むことはない。
# 例: "don't"・"it's"(内部アポストロフィ)、"well-known"(ハイフン複合語)、
# "g2p"・"COVID-19"(英数字混在語)はいずれも1トークンとして切り出される。
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")


@dataclass(frozen=True)
class Token:
    text: str
    is_word: bool


def tokenize(text: str) -> list[Token]:
    """テキストを Token のリストに分割する。

    英単語以外の文字(空白・改行・句読点・日本語・数字のみの文字列など)は
    変更されず、連続する部分がまとめて1つの非単語トークンになる。
    すべてのTokenのtextを結合すると元のtextに一致する(ラウンドトリップ可能)。
    """
    tokens: list[Token] = []
    non_word_buffer: list[str] = []
    pos = 0

    def flush_non_word() -> None:
        if non_word_buffer:
            tokens.append(Token("".join(non_word_buffer), is_word=False))
            non_word_buffer.clear()

    for match in _TOKEN_PATTERN.finditer(text):
        start, end = match.span()
        if start > pos:
            non_word_buffer.append(text[pos:start])
        matched = match.group()
        # アルファベットを1文字も含まない候補(例: "123-456")は英単語とみなさず、
        # 前後の非単語文字列とまとめて保持する。
        if any(c.isalpha() for c in matched):
            flush_non_word()
            tokens.append(Token(matched, is_word=True))
        else:
            non_word_buffer.append(matched)
        pos = end
    if pos < len(text):
        non_word_buffer.append(text[pos:])
    flush_non_word()
    return tokens
