import pytest

from katakana_eigo.data.phoneme_kana_map import (
    CONSONANT_MAP,
    VOWEL_MAP,
    normalize_phoneme,
)

ARPABET_VOWELS = {
    "AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER",
    "EY", "IH", "IY", "OW", "OY", "UH", "UW",
}

ARPABET_CONSONANTS = {
    "B", "CH", "D", "DH", "F", "G", "HH", "JH", "K", "L", "M", "N",
    "NG", "P", "R", "S", "SH", "T", "TH", "V", "W", "Y", "Z", "ZH",
}


def test_vowel_map_covers_all_arpabet_vowels():
    assert set(VOWEL_MAP.keys()) == ARPABET_VOWELS


def test_consonant_map_covers_all_arpabet_consonants():
    assert set(CONSONANT_MAP.keys()) == ARPABET_CONSONANTS


def test_consonant_map_has_all_five_columns():
    for consonant, row in CONSONANT_MAP.items():
        assert set(row.keys()) == {"a", "i", "u", "e", "o"}, consonant


@pytest.mark.parametrize(
    "phoneme, kana",
    [
        ("IY", "イー"),
        ("EY", "エイ"),
        ("AY", "アイ"),
        ("ER", "アー"),
    ],
)
def test_representative_vowel_entries(phoneme, kana):
    assert VOWEL_MAP[phoneme].kana == kana


@pytest.mark.parametrize(
    "consonant, column, kana",
    [
        ("T", "i", "ティ"),
        ("D", "i", "ディ"),
        ("V", "a", "ヴァ"),
        ("F", "a", "ファ"),
        ("L", "u", "ル"),
        ("R", "u", "ル"),
    ],
)
def test_representative_consonant_entries(consonant, column, kana):
    assert CONSONANT_MAP[consonant][column] == kana


@pytest.mark.parametrize(
    "phoneme, expected",
    [
        ("AH0", ("AH", 0)),
        ("IY1", ("IY", 1)),
        ("EY2", ("EY", 2)),
        ("K", ("K", None)),
    ],
)
def test_normalize_phoneme(phoneme, expected):
    assert normalize_phoneme(phoneme) == expected
