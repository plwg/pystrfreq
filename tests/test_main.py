import sys
from pathlib import Path

import pytest

from pystrfreq.main import extract_string_from_file, main


def write(tmp_path: Path, name: str, source: str) -> Path:
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    return path


def run(monkeypatch: pytest.MonkeyPatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["pystrfreq", *args])
    main()


def test_extract_strings(tmp_path: Path) -> None:
    path = write(tmp_path, "a.py", 'x = "a"\ny = f"b{x}c"\n')
    assert sorted(extract_string_from_file(path, False)) == ["a", "b", "c"]


def test_ignore_docstring(tmp_path: Path) -> None:
    path = write(tmp_path, "a.py", '"""doc"""\ndef f():\n    """fdoc"""\n    return "doc"\n')
    assert extract_string_from_file(path, True) == ["doc"]


def test_syntax_error_warns(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "bad.py", "def (:\n")
    assert extract_string_from_file(path, False) == []
    assert "bad.py: skipped" in capsys.readouterr().err


def test_source_encoding(tmp_path: Path) -> None:
    path = tmp_path / "enc.py"
    path.write_bytes(b'# -*- coding: latin-1 -*-\nx = "caf\xe9"\n')
    assert extract_string_from_file(path, False) == ["caf\u00e9"]


def test_utf8_bom(tmp_path: Path) -> None:
    path = tmp_path / "bom.py"
    path.write_bytes(b'\xef\xbb\xbfx = "a"\n')
    assert extract_string_from_file(path, False) == ["a"]


def test_invalid_encoding_warns(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.py"
    path.write_bytes(b'x = "\xff"\n')
    assert extract_string_from_file(path, False) == []
    assert "bad.py: skipped" in capsys.readouterr().err


def test_no_python_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run(monkeypatch, str(tmp_path))
    assert capsys.readouterr().out == ""


def test_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    write(tmp_path, "a.py", 'x = "a"\ny = "a"\nz = "b"\n')
    run(monkeypatch, "-m", "2", str(tmp_path))
    assert capsys.readouterr().out == "2 'a'\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="t-strings need Python 3.14+")
def test_template_string(tmp_path: Path) -> None:
    path = write(tmp_path, "t.py", 'n = "w"\nt = t"hi {n}!"\n')
    assert sorted(extract_string_from_file(path, False)) == ["!", "hi ", "w"]
