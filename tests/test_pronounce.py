from katakana_eigo.pronounce import _is_valid_phoneme, word_to_phonemes


def test_known_word_uses_cmu_dict():
    assert word_to_phonemes("hello") == ["HH", "AH0", "L", "OW1"]


def test_known_word_is_case_insensitive():
    assert word_to_phonemes("Hello") == word_to_phonemes("hello")


def test_unknown_word_falls_back_to_g2p():
    phonemes = word_to_phonemes("zzxxqqnotaword")
    assert phonemes
    assert all(_is_valid_phoneme(p) for p in phonemes)


def test_empty_string_returns_empty_list():
    assert word_to_phonemes("") == []


def test_apostrophe_word_resolves_via_dict():
    phonemes = word_to_phonemes("don't")
    assert phonemes == ["D", "OW1", "N", "T"]
