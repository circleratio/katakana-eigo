"""英単語をARPAbet音素列に変換する。

CMU Pronouncing Dictionary をまず引き、収録されていない語(固有名詞・専門用語・
造語など)は grapheme-to-phoneme (g2p_en) による推定にフォールバックする。
"""

import pronouncing

from katakana_eigo.data.phoneme_kana_map import CONSONANT_MAP, VOWEL_MAP, normalize_phoneme

_VALID_PHONEME_BASES = set(VOWEL_MAP) | set(CONSONANT_MAP)

_g2p_instance = None


def _get_g2p():
    """g2p_en.G2p はモデル読み込みのコストが大きいため遅延・使い回しする。"""
    global _g2p_instance
    if _g2p_instance is None:
        from g2p_en import G2p

        _g2p_instance = G2p()
    return _g2p_instance


def _is_valid_phoneme(token: str) -> bool:
    base, _ = normalize_phoneme(token)
    return base in _VALID_PHONEME_BASES


def word_to_phonemes(word: str) -> list[str]:
    """単語をARPAbet音素列(ストレス数字付き)に変換する。

    どの方法でも発音が得られない場合は空リストを返す。呼び出し側はこれを
    「変換不能」とみなし、元の単語をそのまま出力する。
    """
    candidates = pronouncing.phones_for_word(word)
    if candidates:
        return candidates[0].split()

    try:
        g2p = _get_g2p()
        phonemes = [p for p in g2p(word) if _is_valid_phoneme(p)]
    except Exception:
        return []

    return phonemes
