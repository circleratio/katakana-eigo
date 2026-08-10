"""fixtures/ の入力・期待出力ペアを使ったCLI全体の結合テスト。"""

from pathlib import Path

import pytest

from katakana_eigo.cli import main

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_CASES = sorted(p.name for p in FIXTURES_DIR.iterdir() if p.is_dir())


@pytest.mark.parametrize("case", FIXTURE_CASES)
def test_fixture_case(case, capsys):
    case_dir = FIXTURES_DIR / case
    input_path = case_dir / "input.txt"
    expected = (case_dir / "expected.txt").read_text(encoding="utf-8")

    exit_code = main([str(input_path)])

    assert exit_code == 0
    assert capsys.readouterr().out == expected


def test_fixture_cases_are_not_empty():
    assert FIXTURE_CASES
