import pytest

from katakana_eigo.tokenizer import Token, tokenize


def reconstruct(tokens: list[Token]) -> str:
    return "".join(t.text for t in tokens)


@pytest.mark.parametrize(
    "text",
    [
        "hello world",
        "こんにちは、これは a test です。",
        "I can't find my keys\nWhere did you put them?\n\n",
        "NASA said: 'go!'",
        "",
        "12345 !@#$%",
        "don't give up now",
    ],
)
def test_tokenize_is_roundtrip(text):
    assert reconstruct(tokenize(text)) == text


def test_english_only_words_are_marked_as_word():
    tokens = tokenize("hello world")
    assert [t.text for t in tokens if t.is_word] == ["hello", "world"]


def test_non_word_tokens_are_grouped():
    tokens = tokenize("hello, world!")
    assert tokens == [
        Token("hello", is_word=True),
        Token(", ", is_word=False),
        Token("world", is_word=True),
        Token("!", is_word=False),
    ]


def test_mixed_japanese_and_english():
    text = "これは a pen です"
    tokens = tokenize(text)
    words = [t.text for t in tokens if t.is_word]
    assert words == ["a", "pen"]
    assert reconstruct(tokens) == text


def test_apostrophe_word_kept_as_single_token():
    tokens = tokenize("don't")
    assert tokens == [Token("don't", is_word=True)]


def test_apostrophe_at_boundary_not_absorbed():
    tokens = tokenize("'hello'")
    assert tokens == [
        Token("'", is_word=False),
        Token("hello", is_word=True),
        Token("'", is_word=False),
    ]


def test_newlines_and_punctuation_preserved():
    text = "Can't help but to grow and grow\nAll this love"
    tokens = tokenize(text)
    non_word_text = "".join(t.text for t in tokens if not t.is_word)
    assert "\n" in non_word_text
