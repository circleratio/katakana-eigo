# katakana-eigo

英語の文章を、実際の発音に近いカタカナ表記に変換するCLIフィルタ。

詳細な要件・設計は [`requirement.md`](requirement.md) / [`spec.md`](spec.md) / [`plan.md`](plan.md) を参照。

## セットアップ

```sh
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -e ".[dev]"   # Windows
# source .venv/bin/activate; pip install -e ".[dev]"    # macOS/Linux

python scripts/download_nltk_data.py
```

`g2p_en`(辞書未収録語の発音推定に使用)はNLTKのデータ(`cmudict`, `averaged_perceptron_tagger_eng`)を必要とする。
`scripts/download_nltk_data.py` を一度実行してダウンロードしておくこと。

> 補記: インストール済みのnltkバージョンによっては、g2p_enが期待する
> `averaged_perceptron_tagger` ではなく `averaged_perceptron_tagger_eng` という
> リソース名で検索される場合がある。上記スクリプトは両方の名前の差異を吸収するため、
> 単に `nltk.download('averaged_perceptron_tagger')` だけでは不足することがある点に注意。

## 使い方

```sh
katakana-eigo input.txt
cat input.txt | katakana-eigo
```

例:

```sh
$ echo "Hello world. This is a test." | katakana-eigo
ハロウ ワールド. ジス イズ ア テスト.

$ echo "これは a pen です。Thank you!" | katakana-eigo
これは ア ペン です。サングク ユー!
```

日本語など英語以外の文字はそのまま出力され、改行・句読点・単語区切りも保持される。

## 既知の限界

規則ベースのベストエフォート変換であり、辞書的に定着した外来語表記の再現を目的としていない。

- 定着した外来語表記と一致しない場合がある(例: `stop` → `スタップ`。慣用は `ストップ`)
- L と R はどちらもラ行になり区別されない(標準カタカナの表現力の限界)
- 略語・頭字語(`NASA`, `USA` 等)を1文字ずつ読み上げる特別ルールは無い。大文字小文字を区別しない設計のため大文字パターンからの頭字語検出自体ができず、単なる未対応ではなく設計変更が必要な恒常的な限界

詳細は [`requirement.md`](requirement.md) の「既知の限界」、[`spec.md`](spec.md) 8章を参照。

## プロジェクト構成

```
katakana_eigo/
├── cli.py                   # エントリポイント(パイプライン統合)
├── io_utils.py               # 標準入出力/ファイルの読み書き
├── tokenizer.py               # 英単語/非英単語のトークン分割
├── pronounce.py                # 単語 → ARPAbet音素列(CMU辞書 + g2p_enフォールバック)
├── kana.py                     # 音素列 → カタカナ変換ルール
└── data/phoneme_kana_map.py     # ARPAbet ↔ カタカナ対応テーブル
tests/                           # 単体テスト + fixtures/ による結合テスト
scripts/download_nltk_data.py    # g2p_en用NLTKデータの取得スクリプト
```

## 開発状況

`plan.md` の Phase 0〜9(環境構築〜要件変更対応)まで完了。Phase 10(出力ファイルオプション等)は将来対応でスコープ外。

## テスト

```sh
./.venv/Scripts/python.exe -m pytest
```
