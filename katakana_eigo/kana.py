"""ARPAbet音素列をカタカナ表記に変換する。

基本方針:
  - 子音 + 母音 は `CONSONANT_MAP[子音][母音のcolumn] + 母音.kana[1:]` で合成する
    (母音の先頭仮名を子音側の行に置き換え、残りの仮名(長音・二重母音の後半)を
    そのまま付け足す)。例: T + IY("イー") -> "ティ" + "ー" = "ティー"。
  - 母音が続かない子音(語末・子音クラスタ)は、既定の行("u"列。T/Dのみ"o"列)を
    使って母音を補う(例: desk -> デスク)。
  - N が母音を伴わない場合は撥音「ン」にする(例: pen -> ペン。"ヌ"にはしない)。
  - 語末の無声破裂音/破擦音(P T K CH)が短母音の直後に来る場合は、促音「ッ」を
    前置する(例: cat -> カット, book -> ブック)。長母音・二重母音の後には適用しない
    (例: like -> ライク)。
  - 母音の直後で後続母音を伴わない R は、独立した子音としてではなく直前母音の
    長音として扱う(例: car -> カー, party -> パーティー)。アメリカ英語の
    Rカラー母音を反映するための簡略ルール。
  - ストレス(強勢)は母音の選択には使用しない。無強勢母音(シュワー等)も
    対応する母音と同じ仮名で表現する(簡略化)。

これらは実際の外来語表記の慣習と完全には一致しない(例: stop は "ストップ" ではなく
本ルールでは "スタップ" になる)。本ツールは辞書的な定着表記の再現ではなく、
綴り/発音からの規則的なベストエフォート変換を目的とするための既知の割り切りである。
"""

from katakana_eigo.data.phoneme_kana_map import CONSONANT_MAP, VOWEL_MAP, normalize_phoneme

_DEFAULT_EPENTHETIC_COLUMN = "u"
_EPENTHETIC_COLUMN_OVERRIDES = {"T": "o", "D": "o"}
_GEMINATION_CONSONANTS = {"P", "T", "K", "CH"}
_SHORT_VOWELS = {base for base, v in VOWEL_MAP.items() if len(v.kana) == 1}


def _epenthetic_mora(consonant: str) -> str:
    if consonant == "N":
        return "ン"
    if consonant == "NG":
        return "ング"
    column = _EPENTHETIC_COLUMN_OVERRIDES.get(consonant, _DEFAULT_EPENTHETIC_COLUMN)
    return CONSONANT_MAP[consonant][column]


def phonemes_to_kana(phonemes: list[str]) -> str:
    """ARPAbet音素列(ストレス数字付き)をカタカナ文字列に変換する。"""
    normalized = [normalize_phoneme(p) for p in phonemes]
    n = len(normalized)
    out: list[str] = []
    prev_vowel_base: str | None = None
    i = 0
    while i < n:
        base, _stress = normalized[i]

        if base in VOWEL_MAP:
            out.append(VOWEL_MAP[base].kana)
            prev_vowel_base = base
            i += 1
            continue

        if base not in CONSONANT_MAP:
            # word_to_phonemes側でフィルタ済みの前提だが、未知記号は読み飛ばす。
            i += 1
            continue

        next_base = normalized[i + 1][0] if i + 1 < n else None
        if next_base is not None and next_base in VOWEL_MAP:
            vowel = VOWEL_MAP[next_base]
            out.append(CONSONANT_MAP[base][vowel.column] + vowel.kana[1:])
            prev_vowel_base = next_base
            i += 2
            continue

        # 後続に母音が無い子音(語末 or 子音クラスタ)。
        if base == "R" and prev_vowel_base is not None:
            out.append("ー")
        else:
            mora = _epenthetic_mora(base)
            is_word_final = i + 1 == n
            if (
                is_word_final
                and base in _GEMINATION_CONSONANTS
                and prev_vowel_base in _SHORT_VOWELS
            ):
                mora = "ッ" + mora
            out.append(mora)
        prev_vowel_base = None
        i += 1

    return "".join(out)
