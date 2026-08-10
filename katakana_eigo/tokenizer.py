"""入力テキストを英単語トークンとそれ以外のトークンに分割する。"""

import re
from dataclasses import dataclass

# 英単語: アルファベットの連続。内部にアポストロフィを挟んだ続き(don't, it's)も
# 1トークンとして扱う。
_WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*")


@dataclass(frozen=True)
class Token:
    text: str
    is_word: bool


def tokenize(text: str) -> list[Token]:
    """テキストを Token のリストに分割する。

    英単語以外の文字(空白・改行・句読点・日本語など)は変更されず、
    連続する部分がまとめて1つの非単語トークンになる。
    すべてのTokenのtextを結合すると元のtextに一致する(ラウンドトリップ可能)。
    """
    tokens: list[Token] = []
    pos = 0
    for match in _WORD_PATTERN.finditer(text):
        start, end = match.span()
        if start > pos:
            tokens.append(Token(text[pos:start], is_word=False))
        tokens.append(Token(match.group(), is_word=True))
        pos = end
    if pos < len(text):
        tokens.append(Token(text[pos:], is_word=False))
    return tokens
