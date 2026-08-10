import pytest

from katakana_eigo.kana import phonemes_to_kana


@pytest.mark.parametrize(
    "phonemes, expected",
    [
        (["HH", "AH0", "L", "OW1"], "ハロウ"),
        (["L", "AY1", "K"], "ライク"),
        (["D", "EH1", "S", "K"], "デスク"),
        (["K", "AE1", "T"], "カット"),
        (["K", "AA1", "R"], "カー"),
        (["P", "AA1", "R", "T", "IY0"], "パーティー"),
        (["F", "UW1", "D"], "フード"),
        (["B", "AH0", "N", "AE1", "N", "AH0"], "バナナ"),
        (["AH0", "B", "AW1", "T"], "アバウト"),
        (["B", "ER1", "D"], "バード"),
        (["B", "OY1"], "ボイ"),
        (["S", "EY1"], "セイ"),
        (["G", "OW1"], "ゴウ"),
        (["S", "IY1"], "シー"),
        (["M", "AY1"], "マイ"),
        (["HH", "AW1"], "ハウ"),
        (["P", "EH1", "N"], "ペン"),
    ],
)
def test_phonemes_to_kana(phonemes, expected):
    assert phonemes_to_kana(phonemes) == expected


def test_empty_phoneme_list_returns_empty_string():
    assert phonemes_to_kana([]) == ""


def test_gemination_not_applied_after_diphthong():
    # like: 二重母音(AY)の後の語末Kには促音を付けない
    assert phonemes_to_kana(["L", "AY1", "K"]) == "ライク"


def test_gemination_applied_after_short_vowel():
    # cat: 短母音(AE)の後の語末Tには促音「ッ」を付ける
    assert phonemes_to_kana(["K", "AE1", "T"]) == "カット"


def test_coda_r_lengthens_preceding_vowel():
    assert phonemes_to_kana(["K", "AA1", "R"]) == "カー"


def test_word_final_n_becomes_syllabic_n_not_nu():
    assert phonemes_to_kana(["P", "EH1", "N"]) == "ペン"
