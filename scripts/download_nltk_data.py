"""g2p_en が利用するNLTKデータを取得するセットアップスクリプト。

新しいバージョンのnltkでは g2p_en が期待するリソース名(`averaged_perceptron_tagger`)と
実際に検索されるリソース名(`averaged_perceptron_tagger_eng`)が異なるため、
両方を明示的にダウンロードする。
"""

import nltk

RESOURCES = [
    "cmudict",
    "averaged_perceptron_tagger_eng",
]


def main() -> None:
    for resource in RESOURCES:
        nltk.download(resource)


if __name__ == "__main__":
    main()
