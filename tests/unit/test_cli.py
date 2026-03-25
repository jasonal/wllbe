import subprocess
import sys

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


def test_run_module_invokes_main():
    result = subprocess.run(
        [sys.executable, "-m", "wllbe.cli", "demo"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "unknown command: demo" in result.stdout
