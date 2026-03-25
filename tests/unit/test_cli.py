import runpy
import sys

import pytest

from wllbe.cli import main


def test_main_prints_usage_for_no_args(capsys):
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "wllbe <command>" in captured.out


def test_main_handles_unknown_command(capsys):
    exit_code = main(["demo"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "unknown command: demo" in captured.out


def test_run_module_invokes_main(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["python", "demo"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("wllbe.cli", run_name="__main__")
    captured = capsys.readouterr()
    assert "unknown command: demo" in captured.out
    assert excinfo.value.code == 2
