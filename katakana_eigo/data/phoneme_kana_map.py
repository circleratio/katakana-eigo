"""ARPAbet音素とカタカナの対応テーブル。

CMU Pronouncing Dictionary / g2p_en が出力する音素表記(ARPAbet, ストレス数字付き)を
カタカナに変換するための基礎データ。実際の音節グルーピングや長音・促音などの
変換ルールは `katakana_eigo.kana` 側で実装し、本モジュールは対応表の提供に専念する。
"""

from dataclasses import dataclass

# ストレス(強勢)レベル。CMU辞書/g2p_enは母音音素の末尾に付与する。
STRESS_UNSTRESSED = 0
STRESS_PRIMARY = 1
STRESS_SECONDARY = 2


@dataclass(frozen=True)
class VowelKana:
    """ARPAbet母音1つに対応するカタカナ表現。

    column: 直前の子音と結合する際に使う行("a"/"i"/"u"/"e"/"o")。
    kana: 単独(直前に子音が無い場合)で使うカタカナ表記。
          二重母音は2文字以上になる(例: "アイ")。先頭の1文字が `column` の
          母音に対応しており、子音と結合する際はこの先頭文字を子音側の行に
          置き換える。
    """

    column: str
    kana: str


# ARPAbetの母音(15種)。ストレス数字を除いた基本形をキーとする。
VOWEL_MAP: dict[str, VowelKana] = {
    "AA": VowelKana("a", "ア"),  # father
    "AE": VowelKana("a", "ア"),  # cat
    "AH": VowelKana("a", "ア"),  # strut / 無強勢時はkana.py側で弱化を扱う
    "AO": VowelKana("o", "オ"),  # thought
    "AW": VowelKana("a", "アウ"),  # how
    "AY": VowelKana("a", "アイ"),  # my
    "EH": VowelKana("e", "エ"),  # bed
    "ER": VowelKana("a", "アー"),  # bird (Rカラー母音)
    "EY": VowelKana("e", "エイ"),  # say
    "IH": VowelKana("i", "イ"),  # bit
    "IY": VowelKana("i", "イー"),  # see
    "OW": VowelKana("o", "オウ"),  # go
    "OY": VowelKana("o", "オイ"),  # boy
    "UH": VowelKana("u", "ウ"),  # book
    "UW": VowelKana("u", "ウー"),  # food
}

# ARPAbetの子音(24種)。各子音が a/i/u/e/o の母音と結合したときのカタカナ表記。
# 外来語表記で定着している拡張仮名(ティ/ディ/ファ/ヴァ等)を優先的に使用する。
CONSONANT_MAP: dict[str, dict[str, str]] = {
    "B": {"a": "バ", "i": "ビ", "u": "ブ", "e": "ベ", "o": "ボ"},
    "CH": {"a": "チャ", "i": "チ", "u": "チュ", "e": "チェ", "o": "チョ"},
    "D": {"a": "ダ", "i": "ディ", "u": "ドゥ", "e": "デ", "o": "ド"},
    "DH": {"a": "ザ", "i": "ジ", "u": "ズ", "e": "ゼ", "o": "ゾ"},  # 有声th
    "F": {"a": "ファ", "i": "フィ", "u": "フ", "e": "フェ", "o": "フォ"},
    "G": {"a": "ガ", "i": "ギ", "u": "グ", "e": "ゲ", "o": "ゴ"},
    "HH": {"a": "ハ", "i": "ヒ", "u": "フ", "e": "ヘ", "o": "ホ"},
    "JH": {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    "K": {"a": "カ", "i": "キ", "u": "ク", "e": "ケ", "o": "コ"},
    "L": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    "M": {"a": "マ", "i": "ミ", "u": "ム", "e": "メ", "o": "モ"},
    "N": {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    "NG": {"a": "ング", "i": "ング", "u": "ング", "e": "ング", "o": "ング"},
    "P": {"a": "パ", "i": "ピ", "u": "プ", "e": "ペ", "o": "ポ"},
    "R": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    "S": {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    "SH": {"a": "シャ", "i": "シ", "u": "シュ", "e": "シェ", "o": "ショ"},
    "T": {"a": "タ", "i": "ティ", "u": "トゥ", "e": "テ", "o": "ト"},
    "TH": {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},  # 無声th
    "V": {"a": "ヴァ", "i": "ヴィ", "u": "ヴ", "e": "ヴェ", "o": "ヴォ"},
    "W": {"a": "ワ", "i": "ウィ", "u": "ウ", "e": "ウェ", "o": "ウォ"},
    "Y": {"a": "ヤ", "i": "イ", "u": "ユ", "e": "イェ", "o": "ヨ"},
    "Z": {"a": "ザ", "i": "ジ", "u": "ズ", "e": "ゼ", "o": "ゾ"},
    "ZH": {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
}


def normalize_phoneme(phoneme: str) -> tuple[str, int | None]:
    """ARPAbet音素からストレス数字を分離する。

    例: "AH0" -> ("AH", 0), "IY1" -> ("IY", 1), "K" -> ("K", None)
    """
    if phoneme and phoneme[-1].isdigit():
        return phoneme[:-1], int(phoneme[-1])
    return phoneme, None
