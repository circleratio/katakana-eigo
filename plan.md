# 実装計画 (plan.md)

`requirement.md` / `spec.md` を実現するための実装手順。依存の少ないモジュールから積み上げ、各段階でテストを書きながら進める(下位モジュール→パイプライン統合の順)。

## Phase 0: 環境構築 ✅ 完了
- [x] `pyproject.toml` を作成(パッケージ名 `katakana-eigo`、Python 3.10+ を想定)
- [x] 依存ライブラリを登録: `pronouncing`, `g2p_en`, テスト用に `pytest`
- [x] パッケージ雛形を作成: `katakana_eigo/__init__.py`, `katakana_eigo/data/`, `tests/`
- [x] `console_scripts` エントリポイントを設定(`katakana-eigo = katakana_eigo.cli:main`)
- [x] `g2p_en` が利用する NLTK データ(`cmudict`, `averaged_perceptron_tagger_eng`)を取得するセットアップスクリプト `scripts/download_nltk_data.py` を作成し、README に手順を記載
  - 注意: 新しいnltkでは g2p_en が期待する `averaged_perceptron_tagger` ではなく `averaged_perceptron_tagger_eng` が検索されるため、両方名の差異をスクリプト側で吸収した

**完了条件**: `pip install -e .` でインストールでき、空のCLIコマンドが起動する。→ `.venv` を作成し `pip install -e ".[dev]"` でインストール、`katakana-eigo` (stub) 実行で終了コード0、`pytest` で `tests/test_cli.py` 1件通過を確認済み。

## Phase 1: データ層 — `data/phoneme_kana_map.py` ✅ 完了
- [x] ARPAbet母音・子音とかなの対応テーブル(`VOWEL_MAP`, `CONSONANT_MAP`)を定義
  - `VOWEL_MAP`: 母音15種 → `column`(a/i/u/e/o)と単独時のかな表記
  - `CONSONANT_MAP`: 子音24種 → a/i/u/e/o各行のかな表記(外来語表記のティ/ディ/ファ/ヴァ等を採用)
- [x] ストレス(強勢)なしの音素記号への正規化ヘルパー `normalize_phoneme()` を用意(例: `AH0` → `("AH", 0)`)
- [x] 対応表の単体テスト(`tests/test_phoneme_kana_map.py`): ARPAbet全音素の網羅、代表エントリ、`normalize_phoneme` の挙動を検証

**完了条件**: テーブルをimportして代表的な音素をキーに引けることをテストで確認。→ `pytest` 18件通過(Phase0分含む)。

## Phase 2: `tokenizer.py` ✅ 完了
- [x] `Token` データクラス(`text`, `is_word`)を定義
- [x] `tokenize(text: str) -> list[Token]` を実装(正規表現 `[A-Za-z]+(?:'[A-Za-z]+)*` で英単語を切り出し、それ以外はまとめて非単語トークンにする)
- [x] テスト: 英単語のみ / 日英混在 / 改行・句読点混在 / アポストロフィを含む単語(`don't`) / アポストロフィが語境界にある場合(`'hello'`) のケース

**完了条件**: `tokenize` の出力を結合すると元のテキストに完全一致する(ラウンドトリップが取れる)ことをテストで保証。→ `pytest` 31件通過。パラメータ化したラウンドトリップテストで様々な入力(空文字列・記号のみ・日英混在等)を網羅。

## Phase 3: `pronounce.py` ✅ 完了
- [x] `word_to_phonemes(word: str) -> list[str]` を実装
  - [x] CMU辞書検索(`pronouncing.phones_for_word`)、先頭候補を採用
  - [x] 辞書に無い場合は `g2p_en` にフォールバック(モデルは遅延初期化・使い回し)
  - [x] どちらも失敗した場合は空リストを返す
  - [x] g2p_enの出力に混じりうる非音素トークン(スペース等)を `_is_valid_phoneme` で除外
- [x] テスト(`tests/test_pronounce.py`): 辞書収録語(`hello`)、大文字小文字非依存、辞書未収録語(`zzxxqqnotaword`)、空文字列、アポストロフィ語(`don't`)

**完了条件**: 既知単語がCMU辞書由来のARPAbet列を返し、未知語でもg2pにより空でない列(または既知の失敗ケースで空リスト)を返す。→ `pytest` 36件通過。

## Phase 4: `kana.py` ✅ 完了
- [x] 音素列を音節単位(子音+母音、または母音単独)にグルーピングするロジックを実装
  - ルール: `CONSONANT_MAP[子音][母音.column] + 母音.kana[1:]` で合成(長音・二重母音の後半を自然に付加)
- [x] `phonemes_to_kana(phonemes: list[str]) -> str` を実装
- [x] 子音クラスタ・語末の母音補完(既定"u"列、T/Dのみ"o"列。`desk` → `デスク`)を実装
- [x] N が母音を伴わない場合は「ン」(「ヌ」にしない)を実装(`pen` → `ペン`)
- [x] 語末の無声破裂音/破擦音(P T K CH)+ 直前が短母音の場合に促音「ッ」を付与(`cat` → `カット`)。二重母音・長母音の後には付与しない(`like` → `ライク`)
- [x] 母音直後・後続母音なしの R を長音「ー」として扱う(米語のRカラー母音を近似。`car` → `カー`, `party` → `パーティー`)
  - 注: 当初spec.mdで想定したL/Rの区別(共にラ行のまま)は、標準カタカナでは表現手段が乏しいため見送り、既知の制約として明記
- [x] テスト(`tests/test_kana.py`, 22件): `hello`, `like`, `desk`, `cat`, `car`, `party`, `food`, `banana`, `about`, `bird` 等で実単語のCMU音素列から期待カタカナが得られることを検証

**完了条件**: spec.md 3.6 節の代表例を含む単語セットで妥当なカタカナが出力される。→ `pytest` 58件通過。`banana`→`バナナ`, `about`→`アバウト`, `desk`→`デスク`など実際の慣用カタカナと一致。`stop`→`スタップ`(慣用の`ストップ`とは不一致)など、AA音素を一貫して ア列 として扱う簡略化に由来する既知の乖離あり(spec.mdの想定通り、ベストエフォート変換のため許容)。

## Phase 5: `io_utils.py` ✅ 完了
- [x] `read_input(path: str | None) -> str` を実装(標準入力 / ファイル読み込み、UTF-8)
- [x] `write_output(text: str) -> None` を実装(標準出力への書き出し)
- [x] テスト(`tests/test_io_utils.py`): 標準入力からの読み込み、一時ファイルからの読み込み(UTF-8日英混在含む)、存在しないファイルで`FileNotFoundError`、標準出力への書き出し

**完了条件**: ファイル未存在・読み込み権限なしの場合に想定した例外(`FileNotFoundError` 等)が送出される。→ `pytest` 63件通過。

## Phase 6: `cli.py`(パイプライン統合) ✅ 完了
- [x] `argparse` で `[FILE]` 位置引数と `-h/--help` を実装
- [x] `read_input` → `tokenize` → 各単語トークンに `pronounce.word_to_phonemes` → `kana.phonemes_to_kana` を適用 → 非単語トークンと再結合 → `write_output` のパイプラインを実装(`convert_word` / `convert_text`)
- [x] エラーハンドリングを実装(spec.md 6章の表に従い、終了コード 0/1/2 を返す)
- [x] 単語単位の変換失敗時(発音が得られない/変換中の例外)は原文をそのまま残し、処理を継続する

**完了条件**: `echo "hello world" | katakana-eigo` でカタカナが標準出力に出る。存在しないファイルを指定するとエラーメッセージと終了コード1を返す。→ 実際に確認済み。`pytest` 70件通過。

### Phase 6で見つけたバグとその修正
- **UTF-8エンコーディング漏れ**: `io_utils.read_input`/`write_output` が `sys.stdin`/`sys.stdout` の既定エンコーディングに依存しており、この開発環境(Windows)では既定が `cp932` だったため、標準入出力を介すと文字化けする不具合があった(ファイル直接読み書きは `encoding="utf-8"` 明示済みのため無事)。requirement.mdの「入出力の文字エンコーディングはUTF-8とする」に反するため、`sys.stdin`/`sys.stdout` を `reconfigure(encoding="utf-8")` で強制するよう修正(`_force_utf8`)。テストでの `io.StringIO` 差し替えに影響しないよう `hasattr` で存在確認してから呼び出す。

## Phase 7: 結合テスト ✅ 完了
- [x] `tests/fixtures/` に入力txtと期待出力txtのペアを用意
  - `basic`(英語のみ・句読点), `mixed_ja_en`(日英混在), `unknown_word`(辞書未収録語のg2pフォールバック), `apostrophe`(`can't`/`it's`), `multiline`(改行・空行を含む複数行)
  - 期待値はパイプラインの実行結果をそのままゴールデンファイル化(スナップショット方式)。生成時に内容を目視レビュー済み
- [x] `tests/test_integration.py`: `fixtures/` 配下を自動列挙し、`cli.main([入力ファイル])` を実行して標準出力が期待値と一致することを検証(パラメータ化テスト)

**完了条件**: `pytest` で全fixtureが通過する。→ `pytest` 76件通過(結合テスト6件含む)。

### Phase 7で見つけたミスとその修正
- fixture生成スクリプトの初稿でBashのシェルクォート経由でPython文字列リテラルを組み立てた際、アポストロフィのエスケープを誤り `Can't` が `Can''t`(アポストロフィ2つ)になっていた。ヒアドキュメントを使わずシェル経由で複雑な文字列を渡すのは事故りやすいと判明したため、以降はスクリプトファイルを`Write`で作成してから実行する方式に変更した。

## Phase 8: ドキュメント整備 ✅ 完了
- [x] `README.md` を作成(インストール手順、使い方(実行例付き)、`g2p_en` 用NLTKデータの取得方法、既知の限界、プロジェクト構成を含む)
- [x] `requirement.md` の「未確定事項」を全て解消済みとして「確定した事項」に書き換え、新たに判明した「既知の限界」セクションを追加
- [x] `spec.md` 3.5/3.6節を実際の実装(先読み1つの状態機械、促音・コーダR長音化などの規則)に合わせて更新、8章(今後の課題)・9章(テスト方針)を実装結果に合わせて更新

**完了条件**: 初めて触る人が README だけを見てセットアップ〜実行までできる。→ セットアップ手順・実行例・既知の限界・テスト方法を記載。`pytest` 76件通過を最終確認。

### 公開前レビューでの修正
- コミット済み内容を公開可否の観点でレビューしたところ、`input.txt`(サンプルとして置いていた既存ファイル)が実在の楽曲の歌詞と思われる内容であり、`tests/fixtures/multiline/` もその抜粋を使っていたことが判明。著作権上のリスクを避けるため両方を削除し、`multiline` fixtureは自作の英文(改行・空行・句読点を含む)に差し替えた。`pytest` 76件が引き続き通過することを確認。

## Phase 9(将来対応・スコープ外)
- [ ] 出力先ファイル指定オプション(`-o`)
- [ ] 大きな入力に対するストリーミング処理
- [ ] `g2p_en` 依存が重い場合の軽量フォールバックルールの検討
- [ ] 略語(`NASA`, `USA` 等)の個別読み上げルール

これらは spec.md 8章の「今後の課題」に対応し、v1のスコープには含めない。

## 実装順序のまとめ

```
Phase 0 環境構築
   └─ Phase 1 データ層 ─┐
   └─ Phase 2 tokenizer ─┼─ Phase 3 pronounce ─ Phase 4 kana ─┐
   └─ Phase 5 io_utils ──┘                                    ├─ Phase 6 cli(統合)
                                                                └─ Phase 7 結合テスト
                                                                     └─ Phase 8 ドキュメント
```

Phase 1〜5 は互いに依存が薄く並行して着手できるが、Phase 6 (CLI統合) は Phase 2/3/4/5 すべてに依存するため最後にまとめる。
