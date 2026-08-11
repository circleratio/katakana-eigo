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


def test_hyphenated_compound_word_kept_as_single_token():
    tokens = tokenize("well-known")
    assert tokens == [Token("well-known", is_word=True)]


def test_hyphenated_compound_word_with_multiple_hyphens():
    tokens = tokenize("state-of-the-art")
    assert tokens == [Token("state-of-the-art", is_word=True)]


def test_alphanumeric_mixed_word_kept_as_single_token():
    tokens = tokenize("g2p")
    assert tokens == [Token("g2p", is_word=True)]


def test_hyphenated_alphanumeric_word_kept_as_single_token():
    tokens = tokenize("COVID-19")
    assert tokens == [Token("COVID-19", is_word=True)]


def test_digit_only_hyphenated_string_is_not_a_word():
    tokens = tokenize("123-456")
    assert tokens == [Token("123-456", is_word=False)]


def test_digit_only_token_merges_with_surrounding_non_word_text():
    # 数字のみの候補("123-456")は非単語だが、周囲の非単語文字列(スペース・
    # "!")と別々のトークンに分かれず、1つの非単語トークンにまとめられること。
    tokens = tokenize("call 123-456!")
    assert tokens == [
        Token("call", is_word=True),
        Token(" 123-456!", is_word=False),
    ]


def test_multiple_non_word_digit_runs_merge_into_one_token():
    tokens = tokenize("123 456")
    assert tokens == [Token("123 456", is_word=False)]


def test_mid_sentence_dash_not_absorbed_into_words():
    tokens = tokenize("wait - what")
    assert [t.text for t in tokens if t.is_word] == ["wait", "what"]
    assert reconstruct(tokens) == "wait - what"


@pytest.mark.parametrize(
    "text",
    [
        "well-known state-of-the-art tool",
        "g2p and COVID-19 and 123-456",
        "wait - what?",
    ],
)
def test_tokenize_is_roundtrip_for_hyphen_and_digit_cases(text):
    assert reconstruct(tokenize(text)) == text
